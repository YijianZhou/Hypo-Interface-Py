""" Make input station file for HypoDD
"""
import os
import config

# i/o paths
cfg = config.Config()
fsta = cfg.fsta
fout = 'input/station.dat'
f=open(fsta); lines=f.readlines(); f.close()
fout=open(fout,'w')

for line in lines:
    codes = line.split(',')
    net, sta = codes[0].split('.')
    lat = float(codes[1])
    lon = float(codes[2])
    fout.write('{} {} {}\n'.format(sta, lat, lon))
fout.close()
