""" Configure file for hypoDD interface
"""
import os
import numpy as np

class Config(object):
  def __init__(self):

    # 1. format input
    self.fsta_in = 'input/example_station.csv'
    self.fsta_out = 'input/station.dat'
    self.fpha_name = 'input/example_name.pha'
    self.fpha_loc = 'input/example_full.pha'
    self.fpha_reloc = 'input/example_ct_all.pha'
    self.fpha_temp = 'input/example.temp'

    # 2. ph2dt_cc
    # input files
    self.event_root = '/data3/bigdata/zhouyj/example_events_prep'
    self.num_workers = 20
    self.dep_corr = 0 # avoid air quake
    # thres for event pair linking
    self.cc_thres = [0.3, 0.5] # CC thres for event pair
    self.loc_dev_thres = [3, 2] # km, maximum location separation
    self.dist_thres = [150, 150] # km, max epicentral dist
    self.dt_thres = [[1.,1.8], [.6,.8]]
    self.num_sta_thres = [4,4]
    # data preprocess
    self.to_prep = False
    self.freq_band = ['bandpass', [1., 40.]]
    self.samp_rate = 100
    self.chn_p = [[2],[0,1,2]][0] # chn for P picking
    self.chn_s = [[0,1],[0,1,2]][0] # chn for S picking
    self.win_data_p = [1.5,2.5]
    self.win_data_s = [1.,3.]
    self.win_temp_p = [0.2,1.3]
    self.win_temp_s = [0.2,1.8]
    # output file
    self.out_dt = 'input/dt_all.cc'
    self.out_event = 'input/event.dat'

    # 3. format output
    self.out_ctlg = 'output/example_cc.ctlg'
    self.out_pha = 'output/example_cc.pha',
    self.out_pha_all = 'output/example_cc_all.pha'

