""" Calculate differential travel time (dt.cc) by waveform correlation
"""
import sys, os, glob
import time
import numpy as np
from obspy import read, UTCDateTime
from dataset_cc import get_event_list, read_fsta, read_data_temp
import config
from scipy.signal import correlate
from torch.utils.data import Dataset, DataLoader
import torch.multiprocessing as mp
import torch
import warnings
warnings.filterwarnings("ignore")
mp.set_sharing_strategy('file_system')

cfg = config.Config()
# i/o paths
fsta = cfg.fsta
event_root = cfg.event_root
out_dt = open('input/dt_all.cc','w')
# quality control: event pair linking
num_workers = cfg.num_workers
cc_thres = cfg.cc_thres[0] # min cc
loc_dev_thres = cfg.loc_dev_thres[0] # max dev loc
dep_dev_thres = cfg.dep_dev_thres[0] # max dev loc
dist_thres = cfg.dist_thres[0] # max epi-dist
dt_thres = cfg.dt_thres[0] # max dt
num_sta_thres = cfg.num_sta_thres[0] # min sta
temp_mag = cfg.temp_mag
temp_sta = cfg.temp_sta
max_nbr = cfg.max_nbr
# data info
samp_rate = cfg.samp_rate
win_data_p = cfg.win_data_p
win_data_s = cfg.win_data_s
win_temp_p = cfg.win_temp_p
win_temp_s = cfg.win_temp_s
tt_shift_p = win_temp_p[0] - win_data_p[0]
tt_shift_s = win_temp_s[0] - win_data_s[0]
dep_corr = cfg.dep_corr


# calc differential travel time for all event pairs
def calc_dt(event_list, sta_dict, out_dt):
    # 1. get_neighbor_pairs
    print('1. get candidate event pairs')
    num_events = len(event_list)
    dtype = [('lat','O'),('lon','O'),('dep','O'),('is_temp','O'),('sta','O')]
    loc_sta_list = []
    for _, event_loc, pha_dict in event_list:
        sta = list(pha_dict.keys())
        lat, lon, dep, mag = event_loc[1:5]
        is_temp = 1 if mag>=temp_mag and len(sta)>=temp_sta else 0
        loc_sta_list.append((lat, lon, dep, is_temp, sta))
    loc_sta_list = np.array(loc_sta_list, dtype=dtype)
    nbr_dataset = Get_Neighbor(loc_sta_list)
    nbr_loader = DataLoader(nbr_dataset, num_workers=num_workers, batch_size=None)
    t = time.time()
    pair_list = []
    for i, pair_i in enumerate(nbr_loader):
        if i%1000==0: print('done/total events {}/{} | {:.1f}s'.format(i, len(loc_sta_list), time.time()-t))
        pair_list += list(pair_i.numpy())
    pair_list = np.unique(pair_list, axis=0)
    num_pairs = len(pair_list)
    print('%s pairs linked'%num_pairs)
    # 2. calc dt
    print('2. calculate differential travel time (dt.cc)')
    dt_dataset = Diff_TT(event_list, pair_list, sta_dict)
    dt_loader = DataLoader(dt_dataset, num_workers=num_workers, batch_size=None)
    link_num = 0
    t = time.time()
    for i, [[data_evid, temp_evid],dt_dict] in enumerate(dt_loader):
        if i%10000==0: print('done/total {}/{} | {} pairs linked | {:.1f}s'.format(i, num_pairs, link_num, time.time()-t))
        if len(dt_dict)<num_sta_thres: continue
        write_dt(data_evid, temp_evid, dt_dict, out_dt)
        link_num += 1


class Get_Neighbor(Dataset):
  """Dataset for finding neighbor event
  """
  def __init__(self, loc_sta_list):
    self.loc_sta_list = loc_sta_list

  def __getitem__(self, index):
    num_events = len(self.loc_sta_list)
    # 1. select by loc dev
    lat, lon, dep, is_temp, sta_ref = self.loc_sta_list[index]
    cos_lat = np.cos(lat*np.pi/180)
    cond_lat = 111*abs(self.loc_sta_list['lat']-lat) < loc_dev_thres
    cond_lon = 111*abs(self.loc_sta_list['lon']-lon)*cos_lat < loc_dev_thres
    cond_dep = abs(self.loc_sta_list['dep']-dep) < dep_dev_thres
    if is_temp==1: cond_loc = cond_lat*cond_lon*cond_dep
    else: cond_loc = (self.loc_sta_list['is_temp']==1)*cond_lat*cond_lon*cond_dep
    # 2. select by shared sta
    sta_lists = self.loc_sta_list[cond_loc]['sta']
    cond_sta = [len(np.intersect1d(sta_list, sta_ref)) >= num_sta_thres for sta_list in sta_lists]
    # 3. select to maximum num of neighbor
    sub_list = self.loc_sta_list[cond_loc][cond_sta]
    if len(sub_list)==0: return np.array([], dtype=np.int)
    dist_lat = 111*abs(sub_list['lat']-lat)
    dist_lon = 111*abs(sub_list['lon']-lon)*cos_lat
    dist_dep = abs(sub_list['dep']-dep)
    dist_list = (dist_lat**2 + dist_lon**2 + dist_dep**2)**0.5
    dist_thres = np.sort(dist_list)[0:max_nbr+1][-1]
    cond_nbr = dist_list<=dist_thres
    # 4. to pair index
    pair_list = []
    evid_list = np.arange(num_events)[cond_loc][cond_sta][cond_nbr]
    for evid in evid_list:
        if evid==index: continue
        evid1, evid2 = np.sort([evid, index])
        pair_list.append([evid1, evid2])
    return np.array(pair_list, dtype=np.int)

  def __len__(self):
    return len(self.loc_sta_list)


class Diff_TT(Dataset):
  """Dataset for calculating differential travel time (dt.cc)
  """
  def __init__(self, event_list, pair_list, sta_dict):
    self.event_list = event_list
    self.pair_list = pair_list
    self.sta_dict = sta_dict

  def __getitem__(self, index):
    # calc one event pair
    data_idx, temp_idx = self.pair_list[index]
    data_evid, data_loc, pha_dict_data = self.event_list[data_idx]
    temp_evid, temp_loc, pha_dict_temp = self.event_list[temp_idx]
    data_ot, data_lat, data_lon = data_loc[0:3]
    temp_ot, temp_lat, temp_lon = temp_loc[0:3]
    # check loc dev, num sta
    sta_list = [sta for sta in pha_dict_data.keys() if sta in pha_dict_temp.keys()]
    if len(sta_list)<num_sta_thres: return [data_evid, temp_evid], {}
    # for all shared sta pha
    dt_dict = {}
    for sta in sta_list:
        dt_p, dt_s, cc_p, cc_s = [None]*4
        # check epicentral distance
        sta_lat, sta_lon = self.sta_dict[sta]
        data_dist = calc_dist([sta_lat,data_lat], [sta_lon,data_lon])
        temp_dist = calc_dist([sta_lat,temp_lat], [sta_lon,temp_lon])
        if min(data_dist,temp_dist)>dist_thres: continue
        # read data & temp
        data_paths, data_tp, data_ts = pha_dict_data[sta]
        temp_paths, temp_tp, temp_ts = pha_dict_temp[sta]
        data_all, _, data_tt = read_data_temp(data_paths, data_tp, data_ts, data_ot)
        _, temp_all, temp_tt = read_data_temp(temp_paths, temp_tp, temp_ts, temp_ot)
        data_p, data_s, norm_data_p, norm_data_s = data_all
        temp_p, temp_s, norm_temp_p, norm_temp_s = temp_all
        data_ttp, data_tts = data_tt
        temp_ttp, temp_tts = temp_tt
        # calc diff travel time (dt)
        if type(data_p)==np.ndarray and type(temp_p)==np.ndarray:
            cc_p = calc_cc(data_p, temp_p, norm_data_p, norm_temp_p)
            data_ttp += tt_shift_p + np.argmax(cc_p)/samp_rate
            dt_p = data_ttp - temp_ttp 
            cc_p = np.amax(cc_p)
            if cc_p<cc_thres or abs(dt_p)>dt_thres[0]: dt_p, cc_p = [None]*2
        if type(data_s)==np.ndarray and type(temp_s)==np.ndarray:
            cc_s = calc_cc(data_s, temp_s, norm_data_s, norm_temp_s)
            data_tts += tt_shift_s + np.argmax(cc_s)/samp_rate
            dt_s = data_tts - temp_tts 
            cc_s = np.amax(cc_s)
            if cc_s<cc_thres or abs(dt_s)>dt_thres[1]: dt_s, cc_s = [None]*2
        if dt_p or dt_s: dt_dict[sta] = [dt_p, dt_s, cc_p, cc_s]
    return [data_evid, temp_evid], dt_dict

  def __len__(self):
    return len(self.pair_list)


""" base functions
"""

def calc_cc(data, temp, norm_data, norm_temp):
    num_chn, len_data = data.shape
    _,       len_temp = temp.shape
    cc = []
    for i in range(num_chn):
        cci = correlate(data[i], temp[i], mode='valid')[1:]
        cci /= norm_data[i] * norm_temp[i]
        cci[np.isinf(cci)] = 0.
        cci[np.isnan(cci)] = 0.
        cc.append(cci)
    return np.mean(cc,axis=0)


def calc_dist(lat, lon):
    cos_lat = np.cos(lat[0] * np.pi / 180)
    dx = cos_lat * (lon[1]-lon[0])
    dy = lat[1]-lat[0]
    return 111*(dx**2 + dy**2)**0.5


def write_dt(data_evid, temp_evid, dt_dict, out_dt):
    out_dt.write('# {:9} {:9} 0.0\n'.format(data_evid, temp_evid))
    for net_sta, [dt_p, dt_s, cc_p, cc_s] in dt_dict.items():
        net, sta = net_sta.split('.')
        if dt_p: out_dt.write('{:7} {:8.5f} {:.4f} P\n'.format(sta, dt_p, cc_p**0.5))
        if dt_s: out_dt.write('{:7} {:8.5f} {:.4f} S\n'.format(sta, dt_s, cc_s**0.5))


if __name__ == '__main__':
    mp.set_start_method('spawn', force=True) # 'spawn' or 'forkserver'
    # read event data & sta file
    sta_dict = read_fsta(fsta)
    event_list = get_event_list(event_root)
    # calc & write dt
    calc_dt(event_list, sta_dict, out_dt)
    out_dt.close()

