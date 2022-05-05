# Hypo-Interface-Py
Interface for HypoInverse & HypoDD, implemented with Python. <br>

## HypoInverse Interface
### 1. Files  
1.1 config file  <br>
>config.py <br>
1.2 format transfer  
>mk_sta.py <br>
>mk_pha.py 
>sum2csv.py
1.3 main  
>run_hyp.py

### 2. Usage
    1. modify template hyp control file (if necessary)
    2. manually write velo mod (e.g., CRE file), include ref ele if necessary
    3. set i/o paths & weighting params in config file
    4. python run_hyp.py

  Output:
    csv catalog & phase files
    summary file (hyp)

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
    