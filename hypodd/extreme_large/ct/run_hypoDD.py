# 1. run ph2dt (ct)
import os, shutil
import numpy as np
import multiprocessing as mp
from obspy import UTCDateTime
import config

# reloc config
cfg = config.Config()
ctlg_code = cfg.ctlg_code
dep_corr = cfg.dep_corr
fpha = cfg.fpha_in
num_grids = cfg.num_grids
num_workers = cfg.num_workers

# read fpha with evid
def read_pha(fpha):
    pha_dict = {}
    f=open(fpha); lines=f.readlines(); f.close()
    for line in lines:
        codes = line.split(',')
        if len(codes[0])>=14:
            evid = codes[-1][:-1]
            pha_dict[evid] = []
        else: pha_dict[evid].append(line)
    return pha_dict


def run_ph2dt():
    for i in range(num_grids[0]):
      for j in range(num_grids[1]):
        print('-'*40)
        print('run ph2dt: grid %s-%s'%(i,j))
        shutil.copy('input/phase_%s-%s.dat'%(i,j), 'input/phase.dat')
        os.system('ph2dt ph2dt.inp')
        os.system('mv event.sel event.dat dt.ct input')
        os.rename('input/dt.ct','input/dt_%s-%s.ct'%(i,j))
        os.rename('input/event.dat','input/event_%s-%s.dat'%(i,j))
        os.unlink('ph2dt.log')


def run_hypoDD(i,j):
    print('run hypoDD: grid %s-%s'%(i,j))
    # i/o paths
    evid_list = evid_lists[i][j]
    out_ctlg = open('output/%s_%s-%s.ctlg'%(ctlg_code, i,j),'w')
    out_pha = open('output/%s_%s-%s.pha'%(ctlg_code, i,j),'w')
    out_pha_full = open('output/%s_%s-%s_full.pha'%(ctlg_code, i,j),'w')
    write_fin(i,j)
    # 3. run hypoDD
    os.system('hypoDD input/hypoDD_%s-%s.inp'%(i,j))
    # 4. format output
    f=open('output/hypoDD_%s-%s.reloc'%(i,j)); lines=f.readlines(); f.close()
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
        sec = '59.999' if sec=='60.000' else sec
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


def write_fin(i,j):
    fout = open('input/hypoDD_%s-%s.inp'%(i,j),'w')
    f=open('hypoDD.inp'); lines=f.readlines(); f.close()
    for line in lines:
        if 'dt.ct' in line: line = 'input/dt_%s-%s.ct \n'%(i,j)
        if 'event.dat' in line: line = 'input/event_%s-%s.dat \n'%(i,j)
        if 'hypoDD.reloc' in line: line = 'output/hypoDD_%s-%s.reloc \n'%(i,j)
        fout.write(line)
    fout.close()


if __name__ == '__main__':
    # 1. format fpha & fsta
    print('format input files')
    pha_dict = read_pha(fpha)
    os.system('python mk_sta.py')
    os.system('python mk_pha.py')
    evid_lists = np.load('input/evid_lists.npy', allow_pickle=True)
    # 2. run ph2dt
    run_ph2dt()
    # 3. run hypoDD
    idx_list = []
    for i in range(num_grids[0]):
      for j in range(num_grids[1]):
        idx_list.append((i,j))
    pool = mp.Pool(num_workers)
    pool.starmap_async(run_hypoDD, idx_list)
    pool.close()
    pool.join()
    os.unlink('hypoDD.log')
    # 4. merge output
    os.system('cat output/%s_*.ctlg > output/%s.ctlg'%(ctlg_code,ctlg_code))
    os.system('cat output/%s_*.pha > output/%s.pha'%(ctlg_code,ctlg_code))
    os.system('cat output/%s_*_full.pha > output/%s_full.pha'%(ctlg_code,ctlg_code))

