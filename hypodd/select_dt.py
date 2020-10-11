""" Further selection of dt.cc
  Input: dt_all.cc, event_all.dat
    must contain all events, and evid is the index of list
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
nbr_thres = cfg.nbr_thres


""" Base functions
"""
def calc_dist(lat, lon):
    cos_lat = np.cos(lat[0] * np.pi / 180)
    dx = cos_lat * (lon[1]-lon[0])
    dy = lat[1]-lat[0]
    return 111*(dx**2 + dy**2)**0.5


# read fsta
f=open(fsta); lines=f.readlines(); f.close()
sta_dict = {}
for line in lines:
    net_sta, lon, lat, ele = line.split(',')
    sta = net_sta.split('.')[1]
    lat, lon = float(lat), float(lon)
    sta_dict[sta] = [lat, lon]


# raed fevent
print('reading %s'%fevent)
f=open(fevent); lines=f.readlines(); f.close()
event_list = []
for line in lines:
    codes = line.split()
    lat, lon = [float(code) for code in codes[2:4]]
    event_list.append([lat, lon, line])

# read fdt
print('reading %s'%fdt_in)
f=open(fdt_in); lines=f.readlines(); f.close()
dt_list = []
for line in lines:
    codes = line.split()
    if line[0]=='#':
        det_id, temp_id = [int(code) for code in codes[1:3]]
        det_lat, det_lon = event_list[det_id][0:2]
        temp_lat, temp_lon = event_list[temp_id][0:2]
        dt_list.append([[det_id, temp_id], line, []])
    else:
        # select by epicentral distance
        sta = codes[0]
        sta_lat, sta_lon = sta_dict[sta]
        det_dist = calc_dist([sta_lat,det_lat],[sta_lon,det_lon])
        temp_dist = calc_dist([sta_lat,temp_lat],[sta_lon,temp_lon])
        if min(det_dist,temp_dist)>dist_thres: continue
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
evid_list = []
for [[det_id, temp_id], head_line, pha_dt_list] in dt_list:
    # select by loc seperation
    lat1, lon1 = event_list[det_id][0:2]
    lat2, lon2 = event_list[temp_id][0:2]
    loc_dev = calc_dist([lat1,lat2], [lon1,lon2])
    if loc_dev>loc_dev_thres: continue
    sta_list = np.unique([sta for [sta, _] in pha_dt_list])
    if len(sta_list)<num_sta_thres: continue
    evid_list += [det_id, temp_id]
    fdt_out.write(head_line)
    for [_, dt_line] in pha_dt_list: fdt_out.write(dt_line)

fdt_out.close()
