""" Calculate differential travel time (dt.cc) by waveform correlation
"""
import sys, os, glob
import time
import numpy as np
from obspy import read, UTCDateTime
from dataset_ph2dt_cc import read_event
import config
from scipy.signal import correlate
# filter warnings
import warnings
warnings.filterwarnings("ignore")
# torch for multi-processing
from torch.utils.data import Dataset, DataLoader
import torch.multiprocessing as mp
import torch
mp.set_sharing_strategy('file_system')

cfg = config.Config()
# i/o paths
fpha = cfg.fpha_in
fsta = cfg.fsta_in
event_root = cfg.event_root
out_dt = open(cfg.out_dt,'w')
out_event = open(cfg.out_event,'w') if cfg.out_event else None
# thres for linking event pairs
num_workers = cfg.num_workers_calc
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


def read_fsta(fsta):
    f=open(fsta); lines=f.readlines(); f.close()
    sta_dict = {}
    for line in lines:
        net_sta, lon, lat, ele = line.split(',')
        sta = net_sta.split('.')[1]
        lat, lon = float(lat), float(lon)
        sta_dict[sta] = [lat, lon]
    return sta_dict


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

# calc differential travel time for all event pairs
def calc_dt(event_list, sta_dict, out_dt):
    print('calculating differential travel time (dt.cc)')
    # flat corr mat --> pair_list
    num_events = len(event_list)
    pair_list = []
    for i in range(num_events-1):
      for j in range(i+1, num_events):
        pair_list.append([i,j])
    num_pairs = len(pair_list)
    print('%s event pairs in total'%num_pairs)
    # calc dt
    dt_dataset = Diff_TT(pair_list, event_list, sta_dict)
    dt_loader = DataLoader(dt_dataset, num_workers=num_workers, batch_size=None)
    link_num = 0
    t = time.time()
    for i, [[det_idx, temp_idx],dt_dict] in enumerate(dt_loader):
        if i%10000==0: print('done/total {}/{} | {} pairs linked | {:.1f}s'.format(i, num_pairs, link_num, time.time()-t))
        if len(dt_dict) < num_sta_thres: continue
        write_dt(det_idx, temp_idx, dt_dict, out_dt)
        link_num += 1


class Diff_TT(Dataset):
  """Dataset for calculating differential travel time (dt.cc)
  """
  def __init__(self, pair_list, event_list, sta_dict):
    self.pair_list = pair_list
    self.event_list = event_list
    self.sta_dict = sta_dict

  def __getitem__(self, index):
    # calc one event pair
    det_idx, temp_idx = self.pair_list[index]
    det_loc, pha_dict_det = self.event_list[det_idx]
    temp_loc, pha_dict_temp = self.event_list[temp_idx]
    det_lat, det_lon = det_loc[1:3]
    temp_lat, temp_lon = temp_loc[1:3]
    # check loc dev, num sta
    loc_dev = calc_dist([det_lat,temp_lat],[det_lon,temp_lon])
    if loc_dev>loc_dev_thres: return [det_idx, temp_idx], {}
    sta_list = [sta for sta in pha_dict_det.keys() if sta in pha_dict_temp.keys()]
    if len(sta_list)<num_sta_thres: return [det_idx, temp_idx], {}

    # for all shared sta pha
    dt_dict = {}
    for sta in sta_list:
        # check epicentral distance
        sta_lat, sta_lon = self.sta_dict[sta]
        det_dist = calc_dist([sta_lat,det_lat],[sta_lon,det_lon])
        temp_dist = calc_dist([sta_lat,temp_lat],[sta_lon,temp_lon])
        if min(det_dist,temp_dist)>dist_thres: dt_p, cc_p = [None]*2
        # calc diff travel time (dt)
        data_p, data_s, norm_data_p, norm_data_s = pha_dict_det[sta][0]
        temp_p, temp_s, norm_temp_p, norm_temp_s = pha_dict_temp[sta][1]
        det_ttp, det_tts = pha_dict_det[sta][-1]
        temp_ttp, temp_tts = pha_dict_temp[sta][-1]
        if type(data_p)==np.ndarray and type(temp_p)==np.ndarray:
            cc_p = calc_cc(data_p, temp_p, norm_data_p, norm_temp_p)
            det_ttp += tt_shift_p + np.argmax(cc_p)/samp_rate
            dt_p = det_ttp - temp_ttp 
            cc_p = np.amax(cc_p)
            if cc_p<cc_thres: dt_p, cc_p = [None]*2
            elif abs(dt_p)>dt_thres[0]: dt_p, cc_p = [None]*2
        else: dt_p, cc_p = [None]*2
        if type(data_s)==np.ndarray and type(temp_s)==np.ndarray:
            cc_s = calc_cc(data_s, temp_s, norm_data_s, norm_temp_s)
            det_tts += tt_shift_s + np.argmax(cc_s)/samp_rate
            dt_s = det_tts - temp_tts 
            cc_s = np.amax(cc_s)
            if cc_s<cc_thres: dt_s, cc_s = [None]*2
            elif abs(dt_s)>dt_thres[1]: dt_s, cc_s = [None]*2
        else: dt_s, cc_s = [None]*2
        if dt_p or dt_s: dt_dict[sta] = [dt_p, dt_s, cc_p, cc_s]
    return [det_idx, temp_idx], dt_dict

  def __len__(self):
    return len(self.pair_list)


# write dt.cc
def write_dt(det_idx, temp_idx, dt_dict, out_dt):
    out_dt.write('# {:9} {:9} 0.0\n'.format(det_idx, temp_idx))
    for sta, [dt_p, dt_s, cc_p, cc_s] in dt_dict.items():
        if dt_p: out_dt.write('{:7} {:8.5f} {:.4f} P\n'.format(sta, dt_p, cc_p**0.5))
        if dt_s: out_dt.write('{:7} {:8.5f} {:.4f} S\n'.format(sta, dt_s, cc_s**0.5))

# write event.dat
def write_event(event_list, out_event):
    for evid, [event_loc, _] in enumerate(event_list):
        ot, lat, lon, dep, mag = event_loc
        dep += dep_corr
        date = '{:0>4}{:0>2}{:0>2}'.format(ot.year, ot.month, ot.day)
        time = '{:0>2}{:0>2}{:0>2}{:0>2}'.format(ot.hour, ot.minute, ot.second, int(ot.microsecond/1e4))
        loc = '{:7.4f}   {:8.4f}   {:8.3f}  {:4.1f}'.format(lat, lon, dep, mag)
        err_rms = '   0.00    0.00   0.0'
        out_event.write('{}  {}   {} {} {:>10}\n'.format(date, time, loc, err_rms, evid))


if __name__ == '__main__':
    mp.set_start_method('spawn', force=True) # 'spawn' or 'forkserver'

    # read event data & sta file
    event_list = read_event(fpha, event_root)
    sta_dict = read_fsta(fsta)
    # calc & write dt
    calc_dt(event_list, sta_dict, out_dt)
    out_dt.close()
    # write event
    if out_event: 
        write_event(event_list, out_event)
        out_event.close()

