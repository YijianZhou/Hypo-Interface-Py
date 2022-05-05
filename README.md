# Hypo-Interface-Py
Interface for HypoInverse & HypoDD, implemented with Python. <br>

## HypoInverse Interface
#### 1. Files  
1.1 config file  <br>
>*config.py*  <br>

1.2 format transfer  <br>
>*mk_sta.py*, *mk_pha.py*, and *sum2csv.py*  <br>

1.3 main  <br>
>*run_hyp.py*  <br>

1.4 inputs & outputs <br>
>inputs: *eg.pha*, *station_eg.csv*, and *velo_p_eg.cre*  <br>
>outputs: .csv catalog, phase files, and  summary file  <br>

#### 2. Usage
>(0) get event detection (i.e. *.pha*)  <br>
>(1) set i/o paths & hypoInverse parameters in *config.py*  <br>
>(2) manually write velocity model in CRE format (refer to [hypoInverse doc](https://pubs.usgs.gov/of/2002/0171/pdf/of02-171.pdf)) <br>
>(3) *python run_hyp.py*  <br>

## HypoDD Interface  
### Relocation with *dt.ct*  
#### 1. Files
1.1 config file  <br>
>*config.py*, *hypoDD.inp*, and *ph2dt.inp*  <br>

1.2 format transfer  <br>
>*mk_sta.py* and *mk_pha.py*  <br>

1.3 main  <br>
>*run_hypoDD.py*  <br>

1.4 inputs & outputs <br>
>inputs: *eg_hyp_full.pha* and *station_eg.csv* (velocity model is set in hypoDD.inp)  <br>
>outputs: .csv catalog, phase files, and  hypoDD screen prints for each grid  <br>

#### 2. Usage
>(0) get original location (i.e. *_hyp_full.py*) with hypoInverse  <br>
>(1) set i/o paths & location grids in *config.py*  <br>
>(2) set ph2dt & hypoDD parameters (refer to [hypoDD doc](https://www.ldeo.columbia.edu/~felixw/papers/Waldhauser_OFR2001.pdf)) <br>
>(3) *python run_hypoDD.py*  <br>

### Relocation with *dt.cc*  
#### 1. Files
1.1 config file  <br>
>*config.py* and *hypoDD.inp*  <br>

1.2 format transfer  <br>
>*mk_sta.py*, *mk_pha.py*, and *mk_event.py*  <br>

1.3 major functions  <br>
>./preprocess: *cut_events-obspy.py*, *reader.py*, and *signal_lib.py*  <br>
>ph2dt_cc: *ph2dt_cc.py*, *select_dt.py*, and *dataset_cc.py*  <br>

1.4 main  <br>
>*run_hypoDD.py*  <br>

1.5 inputs & outputs <br>
>inputs: *eg.pha*, *eg_hyp_full.pha*, *eg_ct_full.pha* and *station_eg.csv* (velocity model is set in hypoDD.inp)  <br>
>outputs: .csv catalog, phase files, and  hypoDD screen prints for each grid  <br>

#### 2. Usage
>(0) get absolute location (i.e. *_hyp_full.py*) and *dt.ct* relocation (i.e. *_ct_full.py*)  <br>
>(1) set i/o paths, location grids, and ph2dt_cc parameters in *config.py*  <br>
>(2) set hypoDD parameters (refer to [hypoDD doc](https://www.ldeo.columbia.edu/~felixw/papers/Waldhauser_OFR2001.pdf)) <br>
>(3) cut events data in *./preprocess* & *python run_hypoDD.py*  <br>

### Relocation with *dt.ct & dt.cc*  
#### 1. Files
1.1 config file  <br>
>*config.py*, *ph2dt.inp* and *hypoDD.inp*  <br>

1.2 format transfer  <br>
>*mk_sta.py*, *mk_pha.py*, and *mk_event.py*  <br>

1.3 major functions  <br>
>./preprocess: *cut_events-obspy.py*, *reader.py*, and *signal_lib.py*  <br>
>ph2dt_cc: *ph2dt_cc.py*, *select_dt.py*, and *dataset_cc.py*  <br>

1.4 main  <br>
>*run_hypoDD.py*  <br>

1.5 inputs & outputs <br>
>inputs: *eg.pha*, *eg_hyp_full.pha*, and *station_eg.csv* (velocity model is set in hypoDD.inp)  <br>
>outputs: .csv catalog, phase files, and  hypoDD screen prints for each grid  <br>

#### 2. Usage
>(0) get original location (i.e. *_hyp_full.py*) with hypoInverse  <br>
>(1) set i/o paths, location grids, and ph2dt_cc parameters in *config.py*  <br>
>(2) set ph2dt & hypoDD parameters (refer to [hypoDD doc](https://www.ldeo.columbia.edu/~felixw/papers/Waldhauser_OFR2001.pdf)) <br>
>(3) cut events data in *./preprocess* & *python run_hypoDD.py*  <br>