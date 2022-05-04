""" Make input station file for HypoDD
"""
import config

# i/o paths
cfg = config.Config()
fout=open('input/station.dat','w')

f=open(cfg.fsta); lines=f.readlines(); f.close()
for line in lines:
    codes = line.split(',')
    net, sta = codes[0].split('.')
    lat, lon = [float(code) for code in codes[1:3]]
    fout.write('{} {} {}\n'.format(sta, lat, lon))
fout.close()
