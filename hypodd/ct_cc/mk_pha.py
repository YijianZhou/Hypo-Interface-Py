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
fpha_name = cfg.fpha_name
fpha_loc = cfg.fpha_loc
fout = open(cfg.fpha_temp,'w')
ot_min, ot_max = [UTCDateTime(date) for date in cfg.ot_range.split('-')]
lat_min, lat_max = cfg.lat_range
lon_min, lon_max = cfg.lon_range

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

# 2. get loc
f=open(fpha_loc); lines=f.readlines(); f.close()
for line in lines:
    codes = line.split(',')
    if len(codes[0])>=10: 
        evid = codes[-1][:-1]
        event_name = event_dict[evid]
        id_name = '%s_%s'%(evid, event_name)
        ot = UTCDateTime(codes[0])
        lat, lon, dep, mag = [float(code) for code in codes[1:5]]
        if lat_min<lat<lat_max and lon_min<lon<lon_max and ot_min<ot<ot_max: to_add=True
        else: to_add = False; continue
        fout.write('{},{},{},{},{},{}\n'.format(id_name,ot,lat,lon,dep,mag))
    else: 
        if to_add: fout.write(line)
fout.close()
