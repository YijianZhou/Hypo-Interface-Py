""" Configure file for hypoDD interface
"""
import os
import numpy as np


class Config(object):
  def __init__(self):

    self.hypo_root = '/home/zhouyj/bin'
    self.ctlg_code = 'eg_ct'
    self.fsta = 'input/station_eg.csv'
    self.fpha = 'input/eg_hyp_full.pha'
    self.dep_corr = 5 # avoid air quake
    self.ot_range = '20190704-20190710'
    self.lat_range = [35.45,36.05]
    self.lon_range = [-117.8,-117.25]
    self.num_grids = [1,1] # x,y (lon, lat)
    self.xy_pad = [0.056,0.046] # degree
    self.num_workers = 1
    self.keep_grids = False

