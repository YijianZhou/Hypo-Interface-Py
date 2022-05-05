""" Make phase file for ph2dt_cc
"""
import sys
sys.path.append('/home/zhouyj/software/data_prep')
import numpy as np
from reader import dtime2str
from obspy import UTCDateTime
import config

# i/o paths
cfg = config.Config()
dep_corr = cfg.dep_corr
fpha_name = cfg.fpha_name
fpha_loc = cfg.fpha_loc
fout_temp = open('input/phase.temp','w')
# grid params
ot_min, ot_max = [UTCDateTime(date) for date in cfg.ot_range.split('-')]
lat_min, lat_max = cfg.lat_range
lon_min, lon_max = cfg.lon_range
xy_pad = cfg.xy_pad
num_grids = cfg.num_grids
lon_min -= xy_pad[0]
lon_max += xy_pad[0]
lat_min -= xy_pad[1]
lat_max += xy_pad[1]
# phase file for each grid
fouts, evid_lists = [], []
for i in range(num_grids[0]):
  evid_lists.append([])
  for j in range(num_grids[1]):
    evid_lists[i].append([])
    fouts.append(open('input/phase_%s-%s.dat'%(i,j),'w'))
dx = (lon_max - lon_min) / num_grids[0]
dy = (lat_max - lat_min) / num_grids[1]

# 1. write fpha_temp
event_dict = {}
f=open(fpha_name); lines=f.readlines(); f.close()
evid = 0
for line in lines:
    codes = line.split(',')
    if len(codes[0])<10: continue
    event_name = dtime2str(UTCDateTime(codes[0]))
    event_dict[str(evid)] = event_name
    evid += 1

f=open(fpha_loc); lines=f.readlines(); f.close()
for line in lines:
    codes = line.split(',')
    if len(codes[0])>=10: 
        evid = codes[-1][:-1]
        event_name = event_dict[evid]
        id_name = '%s_%s'%(evid, event_name)
        ot = UTCDateTime(codes[0])
        lat, lon, dep, mag = [float(code) for code in codes[1:5]]
        if lat_min<=lat<=lat_max and lon_min<=lon<=lon_max and ot_min<=ot<=ot_max: to_add=True
        else: to_add = False; continue
        fout_temp.write('{},{},{},{},{},{}\n'.format(id_name,ot,lat,lon,dep,mag))
    else: 
        if to_add: fout_temp.write(line)
fout_temp.close()


# 2. write phase.dat for each grid
def get_fout_idx(lat, lon):
    evid_idx, fout_idx = [], []
    for i in range(num_grids[0]):
      for j in range(num_grids[1]):
        # which phase files to write
        if lon_min+i*dx-xy_pad[0]<lon<=lon_min+(i+1)*dx+xy_pad[0] \
        and lat_min+j*dy-xy_pad[1]<lat<=lat_min+(j+1)*dy+xy_pad[1]:
            fout_idx.append(i*num_grids[1]+j)
        # belong to which grid
        if lon_min+i*dx<lon<=lon_min+(i+1)*dx \
        and lat_min+j*dy<lat<=lat_min+(j+1)*dy:
            evid_idx = [i,j]
    return evid_idx, fout_idx

f=open(fpha_loc); lines=f.readlines(); f.close()
for line in lines:
  codes = line.split(',')
  if len(codes[0])>=14:
    # write head line
    ot = UTCDateTime(codes[0])
    lat, lon, dep, mag = [float(code) for code in codes[1:5]]
    dep += dep_corr
    evid = int(codes[-1])
    evid_idx, fout_idx = get_fout_idx(lat, lon)
    if len(evid_idx)!=0: evid_lists[evid_idx[0]][evid_idx[1]].append(evid)
    if len(fout_idx)==0: continue
    if not ot_min<ot<ot_max: continue
    # format time info
    date = '{:4} {:2} {:2}'.format(ot.year, ot.month, ot.day)
    time = '{:2} {:2} {:5.2f}'.format(ot.hour, ot.minute, ot.second + ot.microsecond/1e6)
    # format loc info
    loc = '{:7.4f} {:9.4f}  {:6.2f} {:4.2f}'.format(lat, lon, dep, mag)
    for idx in fout_idx: fouts[idx].write('# {} {}  {}  0.00  0.00  0.00  {:>9}\n'.format(date, time, loc, evid))
  else:
    if len(fout_idx)==0: continue
    if not ot_min<ot<ot_max: continue
    # write sta pick lines
    sta = codes[0].split('.')[1]
    wp, ws = 1., 1.
    if codes[1]!='-1':
        tp = UTCDateTime(codes[1])
        ttp = tp - ot
        for idx in fout_idx: fouts[idx].write('{:<5}{}{:6.3f}  {:6.3f}   P\n'.format(sta, ' '*6, ttp, wp))
    if codes[2]!='-1':
        ts = UTCDateTime(codes[2])
        tts = ts - ot
        for idx in fout_idx: fouts[idx].write('{:<5}{}{:6.3f}  {:6.3f}   S\n'.format(sta, ' '*6, tts, ws))

np.save('input/evid_lists.npy', evid_lists)
for fout in fouts: fout.close()
