""" Configure file for hypoDD interface
"""
import os
import numpy as np


class Config(object):
  def __init__(self):

    # i/o paths
    self.hypo_root = '/home/zhouyj/bin'
    self.ctlg_code = 'eg_ct'
    self.fsta = 'input/station_eg.csv'
    self.fpha = 'input/eg_hyp_full.pha'
    # run ph2dt & hypoDD 
    self.dep_corr = 5 # avoid air quake, modify velo_mod accordingly
    self.ot_range = '20190704-20190710'
    self.lat_range = [35.45,36.05]
    self.lon_range = [-117.8,-117.25]
    self.num_grids = [1,1] # reloc by grid, x,y (lon, lat)
    self.xy_pad = [0.056,0.046] # additional events in each grid, degree
    self.num_workers = 1 
    self.keep_grids = False # whether keep additional outputs in each grid

