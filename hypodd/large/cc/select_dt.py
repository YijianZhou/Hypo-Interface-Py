""" Further selection of dt.cc
  Input: dt_all.cc, event.dat
"""
import numpy as np
import config

cfg = config.Config()
# i/o paths
fdt_in = 'input/dt_all.cc'
fdt_out = open('input/dt.cc','w')
fevent = 'input/event.dat'
fsta = cfg.fsta_in
# thres for linking event pairs
cc_thres = cfg.cc_thres[1]
loc_dev_thres = cfg.loc_dev_thres[1]
dist_thres = cfg.dist_thres[1]
dt_thres = cfg.dt_thres[1]
num_sta_thres = cfg.num_sta_thres[1]


""" Base functions
"""
def calc_dist(lat, lon):
    cos_lat = np.cos(lat[0] * np.pi / 180)
    dx = cos_lat * (lon[1]-lon[0])
    dy = lat[1]-lat[0]
    return 111*(dx**2 + dy**2)**0.5


# read fsta
sta_dict = {}
f=open(fsta); lines=f.readlines(); f.close()
for line in lines:
    net_sta, lat, lon, ele = line.split(',')
    sta = net_sta.split('.')[1]
    lat, lon = float(lat), float(lon)
    sta_dict[sta] = [lat, lon]


# read event.dat
print('reading %s'%fevent)
event_dict = {}
f=open(fevent); lines=f.readlines(); f.close()
for line in lines:
    codes = line.split()
    lat, lon = [float(code) for code in codes[2:4]]
    evid = codes[-1]
    event_dict[evid] = [lat, lon]


# read dt.cc
print('reading %s'%fdt_in)
dt_list = []
f=open(fdt_in); lines=f.readlines(); f.close()
for i,line in enumerate(lines):
    if i%1e6==0: print('done/total %s/%s | %s pairs selected'%(i,len(lines),len(dt_list)))
    codes = line.split()
    if line[0]=='#':
        data_id, temp_id = codes[1:3]
        data_lat, data_lon = event_dict[data_id][0:2]
        temp_lat, temp_lon = event_dict[temp_id][0:2]
        # 1. select loc dev
        to_add = True
        loc_dev = calc_dist([data_lat,temp_lat], [data_lon,temp_lon])
        if loc_dev>loc_dev_thres: to_add = False; continue
        dt_list.append([[data_id, temp_id], line, []])
    else:
        if not to_add: continue
        # 2. select by epicentral distance
        sta = codes[0]
        sta_lat, sta_lon = sta_dict[sta]
        data_dist = calc_dist([sta_lat,data_lat], [sta_lon,data_lon])
        temp_dist = calc_dist([sta_lat,temp_lat], [sta_lon,temp_lon])
        if min(data_dist, temp_dist)>dist_thres: continue
        # select by CC
        dt, wht = [float(code) for code in codes[1:3]]
        cc = wht**2
        pha = codes[-1]
        if cc<cc_thres: continue
        # select by dt value
        if pha=='P' and abs(dt)>dt_thres[0]: continue
        if pha=='S' and abs(dt)>dt_thres[1]: continue
        dt_list[-1][-1].append([sta, line])

# write dt.cc
print('write input/dt.cc')
for [[data_id, temp_id], head_line, pha_dt_list] in dt_list:
    sta_list = np.unique([sta for [sta, _] in pha_dt_list])
    if len(sta_list)<num_sta_thres: continue
    fdt_out.write(head_line)
    for [_, dt_line] in pha_dt_list: fdt_out.write(dt_line)
fdt_out.close()
