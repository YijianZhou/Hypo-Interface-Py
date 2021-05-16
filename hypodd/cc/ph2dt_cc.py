""" Calculate differential travel time (dt.cc) by waveform correlation
"""
import sys, os, glob
import time
import numpy as np
from obspy import read, UTCDateTime
from dataset_ph2dt_cc import get_event_list, read_fsta, read_data_temp
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
fpha_temp = cfg.fpha_temp
fsta = cfg.fsta
event_root = cfg.event_root
out_dt = open('input/dt_all.cc','w')
# quality control: event pair linking
num_workers = cfg.num_workers
cc_thres = cfg.cc_thres[0] # min cc
loc_dev_thres = cfg.loc_dev_thres[0] # max dev loc
dist_thres = cfg.dist_thres[0] # max epi-dist
dt_thres = cfg.dt_thres[0] # max dt
num_sta_thres = cfg.num_sta_thres[0] # min sta
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
    print('get candidate pair_list (select by loc)')
    num_events = len(event_list)
    dtype = [('lat','O'),('lon','O'),('sta','O')]
    loc_sta_list =  np.array([(event_loc[1], event_loc[2], list(pha_dict.keys())) \
        for _,event_loc,pha_dict in event_list], dtype=dtype)
    t = time.time()
    args = [(i, loc_sta_list, num_events) for i in range(num_events-1)]
    pool = mp.Pool(num_workers)
    out = pool.starmap_async(get_neighbor_pairs, args, chunksize=1)
    pool.close()
    while True:
        if out.ready(): break
        num_done = num_events-1 - out._number_left
        print('done/total {}/{} | time {:.1f}s'.format(num_done, num_events-1, time.time()-t))
        time.sleep(10)
    pool.join()
    pair_list = np.concatenate([pair_i for pair_i in out.get()])
    num_pairs = len(pair_list)
    print('%s pairs linked'%num_pairs)

    # 2. calc dt
    print('calculating differential travel time (dt.cc)')
    dt_dataset = Diff_TT(event_list, pair_list, sta_dict)
    dt_loader = DataLoader(dt_dataset, num_workers=num_workers, batch_size=None)
    link_num = 0
    t = time.time()
    for i, [[data_evid, temp_evid],dt_dict] in enumerate(dt_loader):
        if i%10000==0: print('done/total {}/{} | {} pairs linked | {:.1f}s'.format(i, num_pairs, link_num, time.time()-t))
        if len(dt_dict)<num_sta_thres: continue
        write_dt(data_evid, temp_evid, dt_dict, out_dt)
        link_num += 1


class Diff_TT(Dataset):
  """Dataset for calculating differential travel time (dt.cc)
  """
  def __init__(self, event_list, pair_list, sta_dict):
    self.event_list = event_list
    self.pair_list = pair_list
    self.num_events = len(event_list)
    self.sta_dict = sta_dict
    self.cum_num_rows = np.cumsum(np.arange(self.num_events-1,0,-1))

  def __getitem__(self, index):
    # calc one event pair
    pair_idx = self.pair_list[index]
    data_idx = np.where(pair_idx+1<=self.cum_num_rows)[0][0]
    temp_idx = (pair_idx+1-self.cum_num_rows[data_idx-1]) + data_idx if data_idx>0 else pair_idx+1
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


def get_neighbor_pairs(i, loc_sta_list, num_events):
    # 1. select by loc dev
    cos_lat = np.cos(loc_sta_list[i]['lat']*np.pi/180)
    cond_lat = 111*abs(loc_sta_list[i+1:]['lat']-loc_sta_list[i]['lat']) < loc_dev_thres
    cond_lon = 111*abs(loc_sta_list[i+1:]['lon']-loc_sta_list[i]['lon'])*cos_lat < loc_dev_thres
    # 2. select by shared sta
    sta_ref = loc_sta_list[i]['sta']
    sta_lists = loc_sta_list[i+1:][cond_lat*cond_lon]['sta']
    sta_cond = [j for j in range(len(sta_lists)) \
        if len(np.intersect1d(sta_lists[j],sta_ref))>=num_sta_thres]
    sum_row = sum(np.arange(num_events-1,0,-1)[0:i]) if i>0 else 0
    return sum_row + np.where(cond_lat*cond_lon==1)[0][sta_cond]


# write dt.cc
def write_dt(data_evid, temp_evid, dt_dict, out_dt):
    out_dt.write('# {:9} {:9} 0.0\n'.format(data_evid, temp_evid))
    for net_sta, [dt_p, dt_s, cc_p, cc_s] in dt_dict.items():
        sta = net_sta.split('.')[1]
        if dt_p: out_dt.write('{:7} {:8.5f} {:.4f} P\n'.format(sta, dt_p, cc_p**0.5))
        if dt_s: out_dt.write('{:7} {:8.5f} {:.4f} S\n'.format(sta, dt_s, cc_s**0.5))


if __name__ == '__main__':
    mp.set_start_method('spawn', force=True) # 'spawn' or 'forkserver'
    # read event data & sta file
    sta_dict = read_fsta(fsta)
    event_list = get_event_list(fpha_temp, event_root)
    # calc & write dt
    calc_dt(event_list, sta_dict, out_dt)
    out_dt.close()

