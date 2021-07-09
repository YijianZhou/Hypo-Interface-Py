""" run_hypoDD (main)
"""
import os
import shutil
import glob
import numpy as np
from torch.utils.data import Dataset, DataLoader
from obspy import UTCDateTime
import config

# reloc config
cfg = config.Config()
ctlg_code = cfg.ctlg_code
dep_corr = cfg.dep_corr
fpha = cfg.fpha_temp
num_grids = cfg.num_grids
num_workers = cfg.num_workers
keep_grids = cfg.keep_grids
hypo_root = cfg.hypo_root


# read fpha with evid
def read_pha(fpha):
    pha_dict = {}
    f = open(fpha); lines=f.readlines(); f.close()
    for line in lines:
        codes = line.split(',')
        if len(codes[0]) >= 14:
            evid = codes[0].split('_')[0]
            pha_dict[evid] = []
        else: pha_dict[evid].append(line)
    return pha_dict


# write hypoDD input file
def write_fin(i, j):
    fout = open('input/hypoDD_%s-%s.inp'%(i, j), 'w')
    f = open('hypoDD.inp'); lines=f.readlines(); f.close()
    for line in lines:
        if 'event.dat' in line: line = 'input/event_%s-%s.dat \n'%(i, j)
        if 'hypoDD.reloc' in line: line = 'output/hypoDD_%s-%s.reloc \n'%(i, j)
        fout.write(line)
    fout.close()


class Run_HypoDD(Dataset):
  """ Dataset for running HypoDD
  """
  def __init__(self, idx_list):
    self.idx_list = idx_list

  def __getitem__(self, index):
    # i/o paths
    i, j = self.idx_list[index]
    evid_list = evid_lists[i][j]
    out_ctlg = open('output/%s_%s-%s.ctlg'%(ctlg_code, i, j), 'w')
    out_pha = open('output/%s_%s-%s.pha'%(ctlg_code, i, j), 'w')
    out_pha_full = open('output/%s_%s-%s_full.pha'%(ctlg_code, i, j), 'w')
    write_fin(i, j)
    # run hypoDD
    os.system('%s/hypoDD input/hypoDD_%s-%s.inp > output/%s-%s.hypoDD'%(hypo_root, i, j, i, j))
    # format output
    freloc = 'output/hypoDD_%s-%s.reloc'%(i, j)
    if not os.path.exists(freloc): return
    f = open(freloc); lines=f.readlines(); f.close()
    for line in lines:
        codes = line.split()
        evid = codes[0]
        if int(evid) not in evid_list: continue
        pha_lines = pha_dict[evid]
        # get loc info
        lat, lon, dep = codes[1:4]
        dep = round(float(dep) - dep_corr, 2)
        mag = float(codes[16])
        # get time info
        year, mon, day, hour, mnt, sec = codes[10:16]
        sec = '59.999' if sec == '60.000' else sec
        ot = UTCDateTime('{}{:0>2}{:0>2}{:0>2}{:0>2}{:0>6}'.format(year, mon, day, hour, mnt, sec))
        out_ctlg.write('{},{},{},{},{}\n'.format(ot, lat, lon, dep, mag))
        out_pha.write('{},{},{},{},{}\n'.format(ot, lat, lon, dep, mag))
        out_pha_full.write('{},{},{},{},{},{}\n'.format(ot, lat, lon, dep, mag, evid))
        for pha_line in pha_lines:
            out_pha.write(pha_line)
            out_pha_full.write(pha_line)
    out_ctlg.close()
    out_pha.close()
    out_pha_full.close()

  def __len__(self):
    return len(self.idx_list)


if __name__ == '__main__':
    # 1. run ph2dt_cc
    print('run ph2dt_cc')
    os.system('python mk_sta.py')
    os.system('python mk_pha.py')
    os.system('python mk_event.py')
    os.system('python ph2dt_cc.py')
    os.system('python select_dt.py')
    pha_dict = read_pha(fpha)
    evid_lists = np.load('input/evid_lists.npy', allow_pickle=True)
    if not os.path.exists('output'): os.makedirs('output')
    # 2. run hypoDD
    idx_list = [(i, j) for i in range(num_grids[0]) for j in range(num_grids[1])]
    dataset = Run_HypoDD(idx_list)
    dataloader = DataLoader(dataset, num_workers=num_workers, batch_size=None)
    for i, _ in enumerate(dataloader):
        print('run hypoDD: grid {0[0]}-{0[1]}'.format(idx_list[i]))
    os.unlink('hypoDD.log')
    # 3. merge output
    os.system('cat output/%s_*.ctlg > output/%s.ctlg'%(ctlg_code, ctlg_code))
    os.system('cat output/%s_[0-9]*-*[0-9].pha > output/%s.pha'%(ctlg_code, ctlg_code))
    os.system('cat output/%s_*_full.pha > output/%s_full.pha'%(ctlg_code, ctlg_code))
    # delete grid files
    reloc_grids = glob.glob('output/hypoDD_[0-9]*-*[0-9].reloc*')
    ctlg_grids = glob.glob('output/%s_*.ctlg'%ctlg_code)
    pha_grids = glob.glob('output/%s_[0-9]*-[0-9]*.pha'%ctlg_code)
    input_files = glob.glob('input/hypoDD_*.inp')
    input_files += glob.glob('input/event_*.dat')
    if not keep_grids:
        for reloc_grid in reloc_grids: os.unlink(reloc_grid)
        for ctlg_grid in ctlg_grids: os.unlink(ctlg_grid)
        for pha_grid in pha_grids: os.unlink(pha_grid)
        for input_file in input_files: os.unlink(input_file)

