# 1. ph2dt (ct)
python mk_sta.py
python mk_pha.py
ph2dt ph2dt.inp
mv event.sel event.dat dt.ct input
rm ph2dt.log
# 2. ph2dt (cc)
#python ph2dt_cc.py
#python select_dt.py
