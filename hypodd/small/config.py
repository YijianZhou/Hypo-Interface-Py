""" Configure file for hypoDD interface
"""
import os
import numpy as np

class Config(object):
  def __init__(self):

    # 1. format input
    self.fsta_in = 'input/sm_station.csv'
    self.fsta_out = 'input/station.dat'
    self.fpha_in = 'input/sm_ai_local.pha'
    self.fpha_out = 'input/phase.dat'
    self.dep_corr = 0. # avoid air quake

    # 2. ph2dt_cc
    # input files
    self.event_root = '/data3/bigdata/zhouyj/SM_events/sm_prep'
    self.num_workers_read = 20
    self.num_workers_calc = 10
    self.dep_corr = 0 # avoid air quake
    # thres for event pair linking
    self.cc_thres = [0.3, 0.3] # CC thres for event pair
    self.loc_dev_thres = [3, 3] # km, maximum location separation
    self.dist_thres = [80, 80] # km, max epicentral dist
    self.dt_thres = [[1.,1.5], [1.,1.5]]
    self.num_sta_thres = [4,4]
    self.nbr_thres = [2, 40] #TODO
    # data preprocess
    self.to_prep = False
    self.freq_band = ['bandpass', [1., 40.]]
    self.samp_rate = 100
    self.chn_p = [[2],[0,1,2]][1] # chn for P picking
    self.chn_s = [[0,1],[0,1,2]][1] # chn for S picking
    self.win_data_p = [3.,3.5]
    self.win_data_s = [3.,5.]
    self.win_temp_p = [[0.5,2.],[0.,2.]][0]
    self.win_temp_s = [[0.2,2.8],[0.2,1.8]][0]
    # output file
    self.out_dt = 'input/dt_all.cc'
    self.out_event = [None, 'input/event.dat'][0]

    # 3. format output
    self.out_ctlg = 'output/sm_ai_ct-cc-reloc.ctlg'
    self.out_pha = 'output/sm_ai_ct-cc-reloc.pha'
