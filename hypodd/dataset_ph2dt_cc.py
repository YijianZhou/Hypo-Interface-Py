""" Data pipeline (CPU version)
"""
import os
import glob
import time
import numpy as np
import multiprocessing as mp
from obspy import read, UTCDateTime
import config

cfg = config.Config()
# i/o paths
fpha = cfg.fpha_in
# params
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

def read_event(fpha, event_root):
    # 1. read phase file
    print('reading phase file')
    event_list = read_fpha(fpha)
    num_events = len(event_list)

    # 2. read event data
    print('reading event waveform')
    t=time.time()
    if num_workers==1:
        for evid, event in enumerate(event_list): 
            event_loc, pha_dict_data = read_one_event(event, event_root)
            if evid%100==0: print('read/total events {}/{} | time {:.1f}s'.format(evid, num_events, time.time()-t))
            if len(pha_dict_data)<num_sta_thres: continue
            event_list[evid] = [event_loc, pha_dict_data] # [event_loc, pha_dict]
    else:
        pool = mp.Pool(num_workers)
        args = []
        for evid, event in enumerate(event_list): args.append((event, event_root))
        out =  pool.starmap_async(read_one_event, args, chunksize=1)
        pool.close()
        while True:
            if out.ready(): break
            num_done = num_events - out._number_left
            print('read/total events {}/{} | time {:.1f}s'.format(num_done, num_events, time.time()-t))
            time.sleep(5)
        pool.join()
        for evid, [event_loc, pha_dict_data] in enumerate(out.get()): event_list[evid] = [event_loc, pha_dict_data]
    return event_list


def read_one_event(event, event_root):
    # read one event
    event_name, event_loc, pha_dict_pick = event
    event_dir = os.path.join(event_root, event_name)
    pha_dict_data = {}
    for sta, [tp,ts] in pha_dict_pick.items():
        # read event stream & check time range
        st_paths = sorted(glob.glob(os.path.join(event_dir, '*.%s.*'%sta)))
        if len(st_paths)!=3: continue
        st = read_stream(st_paths)
        if len(st)!=3: continue
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
        else: data_p, temp_p, norm_data_p, norm_temp_p, ttp = [None]*5
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
        else: data_s, temp_s, norm_data_s, norm_temp_s, tts = [None]*5
        pha_dict_data[sta] = [[data_p, data_s, norm_data_p, norm_data_s], 
            [temp_p, temp_s, norm_temp_p, norm_temp_s], [ttp, tts]]
    return event_loc, pha_dict_data


""" Base functions
"""

# read phase file
def read_fpha(fpha):
    f=open(fpha); lines=f.readlines(); f.close()
    event_list = []
    for line in lines:
        codes = line.split(',')
        if len(codes)==5:
            event_name = codes[0]
            ot = UTCDateTime(codes[0])
            lat, lon, dep, mag = [float(code) for code in codes[1:]]
            event_loc = [ot, lat, lon, dep, mag]
            event_list.append([event_name, event_loc, {}])
        else:
            sta = codes[0]
            tp = UTCDateTime(codes[1]) if codes[1]!='-1' else -1
            ts = UTCDateTime(codes[2]) if codes[2][:-1]!='-1' else -1
            event_list[-1][-1][sta] = [tp, ts]
    return event_list


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

