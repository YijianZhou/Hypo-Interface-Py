""" Configure file for hypoDD interface
"""
import os
import numpy as np

class Config(object):
  def __init__(self):

    self.ctlg_code = 'example_ct'
    self.hypo_root = '/home/zhouyj/bin'
    self.fsta = 'input/example.sta'
    self.fpha = 'input/example_full.pha'
    self.dep_corr = 5 # avoid air quake
    self.lat_range = [35.4,36.1]
    self.lon_range = [-117.85,-117.25]
    self.num_grids = [10,10] # x,y (lon, lat)
    self.xy_pad = [0.06,0.05] # degree
    self.num_workers = 10
    self.keep_grids = False

