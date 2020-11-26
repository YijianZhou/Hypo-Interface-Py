""" Data pipeline (CPU version)
"""
import os
import glob
import time
import numpy as np
import multiprocessing as mp
from obspy import read, UTCDateTime
import config

# hypo-params
cfg = config.Config()
num_workers = cfg.num_workers_read
to_prep = cfg.to_prep
samp_rate = cfg.samp_rate
freq_band = cfg.freq_band
win_data_p = cfg.win_data_p
win_data_s = cfg.win_data_s
win_temp_p = cfg.win_temp_p
win_temp_s = cfg.win_temp_s
chn_p = cfg.chn_p
chn_s = cfg.chn_s
npts_data_p = int(samp_rate*sum(win_data_p))
npts_data_s = int(samp_rate*sum(win_data_s))
npts_temp_p = int(samp_rate*sum(win_temp_p))
npts_temp_s = int(samp_rate*sum(win_temp_s))
num_sta_thres = cfg.num_sta_thres[0] # min sta 

# get event list (st_paths)
def get_event_list(fpha, fnames, event_root):
    # 1. read phase file
    print('reading phase file')
    name_dict = read_fnames(fnames)
    event_list = read_fpha(fpha, name_dict)
    num_events = len(event_list)
    # 2. get stream paths
    print('getting event data paths')
    for i, [event_name, event_loc, pha_dict_pick] in enumerate(event_list): 
        if len(pha_dict_pick)<num_sta_thres: continue
        event_dir = os.path.join(event_root, event_name)
        pha_dict = {}
        for sta, [tp,ts] in pha_dict_pick.items():
            # read event stream & check time range
            st_paths = sorted(glob.glob(os.path.join(event_dir, '*.%s.*'%sta)))
            if len(st_paths)!=3: continue
            pha_dict[sta] = [st_paths, tp, ts]
        event_list[i] = [event_loc, pha_dict]
    return event_list


def read_data_temp(st_paths, tp, ts, event_loc):
    # read stream
    st = read_stream(st_paths)
    data_p, temp_p, norm_data_p, norm_temp_p, ttp = [None]*5
    data_s, temp_s, norm_data_s, norm_temp_s, tts = [None]*5
    if len(st)!=3: return [None]*4, [None]*4, [None]*2
    # slice data & temp from stream
    if tp!=-1:
      if tp-max(win_data_p[0],win_temp_p[0])<st[0].stats.starttime \
      or tp+max(win_data_p[1],win_temp_p[1])>st[0].stats.endtime:
        data_p, temp_p, norm_data_p, norm_temp_p, ttp = [None]*5
      else:
        data_p = st2np(st.slice(tp-win_data_p[0], tp+win_data_p[1]), npts_data_p)[chn_p]
        temp_p = st2np(st.slice(tp-win_temp_p[0], tp+win_temp_p[1]), npts_temp_p)[chn_p]
        norm_data_p = calc_norm(data_p, npts_temp_p)
        norm_temp_p = np.array([sum(tr**2)**0.5 for tr in temp_p])
        ttp = tp - event_loc[0]
    if ts!=-1:
      if ts+max(win_data_s[1],win_temp_s[1])>st[0].stats.endtime \
      or ts-max(win_data_s[0],win_temp_s[0])<st[0].stats.starttime:
        data_s, temp_s, norm_data_s, norm_temp_s, tts = [None]*5
      else:
        data_s = st2np(st.slice(ts-win_data_s[0], ts+win_data_s[1]), npts_data_s)[chn_s]
        temp_s = st2np(st.slice(ts-win_temp_s[0], ts+win_temp_s[1]), npts_temp_s)[chn_s]
        norm_data_s = calc_norm(data_s, npts_temp_s)
        norm_temp_s = np.array([sum(tr**2)**0.5 for tr in temp_s])
        tts = ts - event_loc[0]
    return [data_p, data_s, norm_data_p, norm_data_s], [temp_p, temp_s, norm_temp_p, norm_temp_s], [ttp, tts]


""" Base functions
"""

# read phase file (with evid)
def read_fpha(fpha, name_dict):
    f=open(fpha); lines=f.readlines(); f.close()
    event_list = []
    for line in lines:
        codes = line.split(',')
        if len(codes)==6:
            ot = UTCDateTime(codes[0])
            lat, lon, dep, mag = [float(code) for code in codes[1:5]]
            evid = codes[-1][:-1]
            event_name = name_dict[evid]
            event_loc = [ot, lat, lon, dep, mag]
            event_list.append([event_name, event_loc, {}])
        else:
            net, sta = codes[0:2]
            tp = UTCDateTime(codes[2]) if codes[2]!='-1' else -1
            ts = UTCDateTime(codes[3]) if codes[3][:-1]!='-1' else -1
            event_list[-1][-1][sta] = [tp, ts]
    return event_list

# read event name file
def read_fnames(fnames):
    name_dict = {}
    f=open(fnames); lines=f.readlines(); f.close()
    for line in lines:
        evid, event_name = line.split(',')
        name_dict[evid] = event_name[:-1]
    return name_dict

# read sta file
def read_fsta(fsta):
    f=open(fsta); lines=f.readlines(); f.close()
    sta_dict = {}
    for line in lines:
        net_sta, lat, lon, ele, _ = line.split('\t')
        sta = net_sta.split('.')[1]
        lat, lon = float(lat), float(lon)
        sta_dict[sta] = [lat, lon]
    return sta_dict


# stream processing
def preprocess(stream):
    # time alignment
    start_time = max([trace.stats.starttime for trace in stream])
    end_time = min([trace.stats.endtime for trace in stream])
    if start_time>end_time: print('bad data!'); return []
    st = stream.slice(start_time, end_time)
    # resample data
    org_rate = int(st[0].stats.sampling_rate)
    rate = np.gcd(org_rate, samp_rate)
    if rate==1: print('warning: bad sampling rate!'); return []
    decim_factor = int(org_rate / rate)
    resamp_factor = int(samp_rate / rate)
    if decim_factor!=1: st = st.decimate(decim_factor)
    if resamp_factor!=1: st = st.interpolate(samp_rate)
    # filter
    st = st.detrend('demean').detrend('linear').taper(max_percentage=0.05, max_length=10.)
    flt_type, freq_rng = freq_band
    if flt_type=='highpass':
        return st.filter(flt_type, freq=freq_rng)
    if flt_type=='bandpass':
        return st.filter(flt_type, freqmin=freq_rng[0], freqmax=freq_rng[1])

def read_stream(stream_paths):
    stream  = read(stream_paths[0])
    stream += read(stream_paths[1])
    stream += read(stream_paths[2])
    if to_prep: return preprocess(stream)
    else: return stream

def calc_norm(data, npts):
    data_cum = [np.cumsum(di**2) for di in data]
    return np.array([np.sqrt(cumi[npts:]-cumi[:-npts]) for cumi in data_cum])

# format transform
def st2np(stream, npts):
    st_np = np.zeros([len(stream), npts], dtype=np.float64)
    for i,trace in enumerate(stream): st_np[i][0:npts] = trace.data[0:npts]
    return st_np

