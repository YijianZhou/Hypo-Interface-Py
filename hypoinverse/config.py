""" Configure file for HypoInverse interface
"""
import numpy as np

class Config(object):
  def __init__(self):

    # i/o paths
    self.ctlg_code = 'eg_hyp'
    self.fsta = 'input/station_eg.csv'
    self.fpha = 'input/eg.pha'
    self.fsums = 'output/%s-*.sum'%self.ctlg_code
    self.out_ctlg = 'output/%s.ctlg'%self.ctlg_code
    self.out_pha = 'output/%s.pha'%self.ctlg_code
    self.out_pha_full = 'output/%s_full.pha'%self.ctlg_code
    self.out_sum = 'output/%s.sum'%self.ctlg_code
    self.out_bad = 'output/%s_bad.csv'%self.ctlg_code
    self.out_good = 'output/%s_good.csv'%self.ctlg_code
    # location info
    self.lat_code = 'N'
    self.lon_code = 'W'
    self.mag_corr = 2. # hypoInv do not support neg mag
    self.ref_ele = 3 # reference elevation for CRE model, > max_sta_ele
    self.grd_ele = 1.5 # ground elevation, can be set as average sta_ele, modify velo_mod accordingly
    # hypoInverse params
    self.num_workers = 10
    self.ztr_rng = np.arange(0.1,15.1,1)
    self.p_wht = 0 # weight code
    self.s_wht = 1
    self.rms_wht = '4 0.25 1 3'
    self.dist_init = '1 40 1 2'
    self.dist_wht = '4 25 1 3'
    self.wht_code = '1 0.6 0.3 0.2' # weight for each weight code
    self.fhyp_temp = 'temp_hyp/temp_vp-pos.hyp'
    self.pmod = 'input/velo_p_eg.cre'
    self.smod = None # None if no independent S model
    self.pos = 1.73 # provide smod or pos
    self.get_prt = False
    self.get_arc = False
    self.keep_fsums = False # whether get additional outputs

