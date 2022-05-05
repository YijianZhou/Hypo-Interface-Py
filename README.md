# Hypo-Interface-Py
Interface for HypoInverse & HypoDD, implemented with Python. <br>

## HypoInverse Interface
### 1. Files  
1.1 config file  <br>
>*config.py*  <br>

1.2 format transfer  <br>
>*mk_sta.py*, *mk_pha.py*, and *sum2csv.py*  <br>

1.3 main  <br>
>*run_hyp.py*  <br>

1.4 inputs & outputs <br>
>inputs: *eg.pha*, *station_eg.csv*, and *velo_p_eg.cre*  <br>
>outputs: .csv catalog, phase files, and  summary file  <br>

### 2. Usage
>(1) set i/o paths & hypoInverse parameters in *config.py*  <br>
>(2) manually write velocity model in CRE format (refer to [hypoInverse doc](https://pubs.usgs.gov/of/2002/0171/pdf/of02-171.pdf)) <br>
>(3) *python run_hyp.py*  <br>

## HypoDD Interface 
1. dt.ct reloc
1.1 Files
  (1) config file
    config.py
    hypodd.inp
    ph2dt.inp
  (2) format transfer
    mk_sta.py
    mk_pha.py
  (3) main
    run_hypoDD.py
1.2 Usage
  (1) Set parameters
    i/o paths & params in config.py
    ph2dt params in ph2dt.inp
    hypoDD params in hypoDD.inp
  (2) run main
    python run_hypoDD.py

2. dt.cc reloc
2.1 Files
  (1) config file
    config.py
    hypodd.inp
  (2) format transfer
    mk_sta.py
    mk_pha.py
    mk_event.py
  (3) ph2dt_cc
    ph2dt_cc.py
    dataset_ph2dt_cc.py
    select_dt.py
  (3) main
    run_hypoDD.py
2.2 Usage
  (1) Set parameters
    i/o paths & params in config.py
    hypoDD params in hypoDD.inp
  (2) run main
    python run_hypoDD.py

3. dt.ct + dt.cc reloc
3.1 Files
  (1) config file
    config.py
    hypodd.inp
    ph2dt.inp
  (2) format transfer
    mk_sta.py
    mk_pha.py
  (3) ph2dt_cc
    ph2dt_cc.py
    dataset_ph2dt_cc.py
    select_dt.py
  (3) main
    run_hypoDD.py
3.2 Usage
  (1) Set parameters
    i/o paths & params in config.py
    hypoDD params in hypoDD.inp
  (2) run main
    python run_hypoDD.py
    