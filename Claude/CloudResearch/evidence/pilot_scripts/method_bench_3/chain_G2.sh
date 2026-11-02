#!/bin/zsh
set -e
cd "$(dirname $0)"
export OMP_NUM_THREADS=2
nice -n 10 python3 -I run_bench3.py primary,score > run_bench3_G3_primary.log 2>&1
nice -n 10 python3 -I d5_sn8.py > d5_sn8.log 2>&1
nice -n 10 python3 -I run_bench3.py combo > run_bench3_G4_combo.log 2>&1
echo CHAIN_G_DONE
