""" Make phase file for ph2dt_cc
  event_name --> event data dir
  loc pha --> abs_ot
  reloc pha --> lat, lon, dep
"""
import sys
sys.path.append('/home/zhouyj/software/data_prep')
import numpy as np
from reader import dtime2str
from obspy import UTCDateTime
import config

# i/o paths
cfg = config.Config()
fpha_name = cfg.fpha_name
fpha_ot = cfg.fpha_ot
fpha_loc = cfg.fpha_loc
fout = open(cfg.fpha_temp,'w')

# 1. get evid & event_name
event_dict = {}
f=open(fpha_name); lines=f.readlines(); f.close()
evid = 0
for line in lines:
    codes = line.split(',')
    if len(codes[0])<10: continue
    event_name = dtime2str(UTCDateTime(codes[0]))
    event_dict[str(evid)] = event_name
    evid += 1

# 2. get abs_ot
ot_dict = {}
f=open(fpha_ot); lines=f.readlines(); f.close()
for line in lines:
    codes = line.split(',')
    if len(codes[0])<10: continue
    evid = codes[-1][:-1]
    ot_dict[evid] = codes[0]

# 3. get reloc
f=open(fpha_loc); lines=f.readlines(); f.close()
for line in lines:
    codes = line.split(',')
    if len(codes[0])>=10: 
        evid = codes[-1][:-1]
        event_name = event_dict[evid]
        id_name = '%s_%s'%(evid, event_name)
        ot = ot_dict[evid]
        lat, lon, dep, mag = codes[1:5]
        fout.write('{},{},{},{},{},{}\n'.format(id_name,ot,lat,lon,dep,mag))
    else: fout.write(line)
fout.close()
