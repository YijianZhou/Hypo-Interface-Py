""" Configure file for hypoDD interface
"""
import os
import numpy as np

class Config(object):
  def __init__(self):

    self.ctlg_code = 'example'
    self.fsta_in = 'input/example.sta'
    self.fsta_out = 'input/station.dat'
    self.fpha_in = 'input/example.pha'
    self.dep_corr = 5 # avoid air quake
    self.lat_range = [35.4,36.1]
    self.lon_range = [-117.8,-117.2]
    self.num_grids = [8,8] # x,y (lon, lat)
    self.xy_pad = [0.08,0.08] # degree
    self.num_workers = 10

