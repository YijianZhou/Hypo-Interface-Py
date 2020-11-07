""" Configure file for HypoInverse interface
"""
import numpy as np

class Config(object):
  def __init__(self):

    self.ctlg_code = 'example'
    # 1. mk_sta: format station file
    self.fsta_in = 'input/example_station.dat'
    self.fsta_out = 'input/example.sta'
    self.lat_code = 'N'
    self.lon_code = 'E'

    # 2. mk_phs: format phase file
    self.fpha_in = 'input/example.pha'
    self.fpha_out = 'input/example_hypo.phs'
    self.mag_corr = 2. # hypoInv do not support neg mag

    # 3. sum2csv: format output files
    self.ref_ele = 3. # ref ele for CRE mod (max sta ele)
    self.grd_ele = 2. # typical station elevation
    self.fsums = 'output/%s-*.sum'%self.ctlg_code
    self.out_ctlg = 'output/%s.ctlg'%self.ctlg_code
    self.out_pha = 'output/%s.pha'%self.ctlg_code
    self.out_sum = 'output/%s.sum'%self.ctlg_code
    self.out_bad = 'output/%s_bad.csv'%self.ctlg_code
    self.out_good = 'output/%s_good.csv'%self.ctlg_code

    # 4. run_hyp
    self.num_workers = 10
    self.ztr_rng = np.arange(5,10,1)
    self.p_wht = 0 # weight code
    self.s_wht = 1
    self.rms_wht = '4 0.5 1 2'
    self.dist_init = '1 40 1 3'
    self.dist_wht = '4 30 1 3'
    self.wht_code = '1 0.5 0.3 0.2'
    self.fhyp_temp = 'temp_hyp/temp_vp-vs.hyp'
    self.pmod = 'input/example_p.cre'
    self.smod = [None, 'input/example_s.cre'][1]
    self.pos = 1.83 # provide smod or pos
    self.get_prt = False
    self.get_arc = False
    self.keep_fsums = False

