#!/bin/zsh
# Phase G chain after tiles,gates,ida: one heavy process at a time.
set -e
cd "$(dirname $0)"
while pgrep -f "run_bench3.py tiles" > /dev/null; do sleep 20; done
export OMP_NUM_THREADS=2
nice -n 10 python3 -I run_bench3.py flood,pul > run_bench3_G2_flood.log 2>&1
nice -n 10 python3 -I hrc_d5.py > hrc_d5.log 2>&1
nice -n 10 python3 -I run_bench3.py primary,score > run_bench3_G3_primary.log 2>&1
nice -n 10 python3 -I run_bench3.py combo > run_bench3_G4_combo.log 2>&1
echo CHAIN_G_DONE
