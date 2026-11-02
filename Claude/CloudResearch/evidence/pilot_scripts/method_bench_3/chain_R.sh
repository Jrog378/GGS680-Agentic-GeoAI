#!/bin/zsh
set -e
cd "$(dirname $0)"
export OMP_NUM_THREADS=2
nice -n 10 python3 -I run_bench3r.py tiles,gates,ida > run_bench3r_R1.log 2>&1
nice -n 10 python3 -I run_bench3r.py flood,pul > run_bench3r_R2_flood.log 2>&1
nice -n 10 python3 -I run_bench3r.py primary,score > run_bench3r_R3_primary.log 2>&1
nice -n 10 python3 -I run_bench3r.py combo,greyrgb > run_bench3r_R4_combo.log 2>&1
nice -n 10 python3 -I nb_cache.py R > nb_cache_R.log 2>&1
python3 -I decide.py > decide.log 2>&1
python3 -I make_nb.py R > make_nb_R.log 2>&1
echo CHAIN_R_DONE
