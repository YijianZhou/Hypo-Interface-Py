""" Configure file for hypoDD interface
"""

class Config(object):
  def __init__(self):

    # 1. i/o paths
    self.ctlg_code = 'example_ct-cc'
    self.fsta = 'input/example.sta'
    self.fpha_name = 'input/example_name.pha'
    self.fpha_loc = 'input/example_loc.pha'
    self.fpha_temp = 'input/example.temp'
    self.out_ctlg = 'output/%s.ctlg'%self.ctlg_code
    self.out_pha = 'output/%s.pha'%self.ctlg_code
    self.out_pha_full = 'output/%s_full.pha'%self.ctlg_code
    # 2. ph2dt_cc
    # input files
    self.event_root = '/data/Example_events'
    self.num_workers = 20
    self.dep_corr = 5 # avoid air quake
    # thres for event pair linking
    self.cc_thres = [0.3, 0.3] # CC thres for event pair
    self.loc_dev_thres = [8,5] # km, maximum location separation
    self.dist_thres = [150, 150] # km, max epicentral dist
    self.dt_thres = [[1.,1.6], [1,1.8]]
    self.num_sta_thres = [4,4]
    # data preprocess
    self.to_prep = False
    self.freq_band = [1.,40.]
    self.samp_rate = 100
    self.chn_p = [[2],[0,1,2]][0] # chn for P picking
    self.chn_s = [[0,1],[0,1,2]][0] # chn for S picking
    self.win_data_p = [1.5,2.5]
    self.win_data_s = [1.,3.]
    self.win_temp_p = [0.2,1.3]
    self.win_temp_s = [0.2,1.8]
    # 3. run hypoDD
    self.hypo_root = '/home/zhouyj/bin'
    self.ot_range = '20150619-20160515'
    self.lat_range = [27.25,28.5]
    self.lon_range = [84.25,86.75]
    self.num_grids = [4,4] # x,y (lon, lat)
    self.xy_pad = [0.1,0.11] # degree
    self.keep_grids = False

