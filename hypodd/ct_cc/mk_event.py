import warnings
""" Make input event.dat
"""
import numpy as np
from obspy import UTCDateTime
import config
warnings.filterwarnings("ignore")

# i/o paths
cfg = config.Config()
fpha = cfg.fpha_temp
dep_corr = cfg.dep_corr
ot_min, ot_max = [UTCDateTime(date) for date in cfg.ot_range.split('-')]
lat_min, lat_max = cfg.lat_range
lon_min, lon_max = cfg.lon_range
num_grids = cfg.num_grids
xy_pad = cfg.xy_pad
# phase file for each grid
out_events, out_phases, evid_lists = [], [], []
for i in range(num_grids[0]):
  evid_lists.append([])
  for j in range(num_grids[1]):
    evid_lists[i].append([])
    out_events.append(open('input/event_%s-%s.dat'%(i, j), 'w'))
    out_phases.append(open('input/phase_%s-%s.dat'%(i, j), 'w'))
# lat-lon range for each grid
dx = (lon_max - lon_min) / num_grids[0]
dy = (lat_max - lat_min) / num_grids[1]

def get_fout_idx(lat, lon):
    evid_idx, fout_idx = [], []
    for i in range(num_grids[0]):
      for j in range(num_grids[1]):
        # which phase files to write
        if lon_min+i*dx-xy_pad[0]<lon <= lon_min+(i+1)*dx+xy_pad[0] \
        and lat_min+j*dy-xy_pad[1]<lat <= lat_min+(j+1)*dy+xy_pad[1]:
            fout_idx.append(i*num_grids[1]+j)
        # belong to which grid
        if lon_min+i*dx<lon <= lon_min+(i+1)*dx \
        and lat_min+j*dy<lat <= lat_min+(j+1)*dy:
            evid_idx = [i, j]
    return evid_idx, fout_idx

f = open(fpha); lines=f.readlines(); f.close()
for line in lines:
  codes = line.split(',')
  if len(codes[0]) >= 14:
    # write event.dat
    evid = int(codes[0].split('_')[0])
    ot = UTCDateTime(codes[1])
    lat, lon, dep, mag = [float(code) for code in codes[2:6]]
    dep += dep_corr
    evid_idx, fout_idx = get_fout_idx(lat, lon)
    if len(evid_idx) != 0: evid_lists[evid_idx[0]][evid_idx[1]].append(evid)
    if len(fout_idx) == 0: continue
    if not ot_min < ot<ot_max: continue
    date = '{:0>4}{:0>2}{:0>2}'.format(ot.year, ot.month, ot.day)
    time = '{:0>2}{:0>2}{:0>2}{:0>2}'.format(ot.hour, ot.minute, ot.second, int(ot.microsecond/1e4))
    loc = '{:7.4f}   {:8.4f}   {:8.3f}  {:4.1f}'.format(lat, lon, dep, mag)
    err_rms = '   0.00    0.00   0.0'
    for idx in fout_idx:
        out_events[idx].write('{}  {}   {} {} {:>10}\n'.format(date, time, loc, err_rms, evid))
    # write phase.dat
    date = '{:4} {:2} {:2}'.format(ot.year, ot.month, ot.day)
    time = '{:2} {:2} {:5.2f}'.format(ot.hour, ot.minute, ot.second + ot.microsecond/1e6)
    loc = '{:7.4f} {:9.4f}  {:6.2f} {:4.2f}'.format(lat, lon, dep+dep_corr, mag)
    for idx in fout_idx:
        out_phases[idx].write('# {} {}  {}  0.00  0.00  0.00  {:>9}\n'.format(date, time, loc, evid))
  else:
    if len(fout_idx) == 0: continue
    if not ot_min < ot<ot_max: continue
    # write picks in phase.dat
    sta = codes[0].split('.')[1]
    wp, ws = 1., 1.
    if codes[1] != '-1':
        tp = UTCDateTime(codes[1])
        ttp = tp - ot
        for idx in fout_idx: out_phases[idx].write('{:<5}{}{:6.3f}  {:6.3f}   P\n'.format(sta, ' '*6, ttp, wp))
    if codes[2] != '-1':
        ts = UTCDateTime(codes[2])
        tts = ts - ot
        for idx in fout_idx: out_phases[idx].write('{:<5}{}{:6.3f}  {:6.3f}   S\n'.format(sta, ' '*6, tts, ws))

np.save('input/evid_lists.npy', evid_lists)
for fout in out_events: fout.close()
for fout in out_phases: fout.close()

