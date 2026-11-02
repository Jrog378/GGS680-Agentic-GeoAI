## Track B, 891 roads

| arm | TP | FN | FP | TN | accuracy | accuracy 95% CI | precision | recall | dry kept dry | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DINOv2 cues | 369 | 96 | 158 | 268 | 0.715 | 0.67-0.76 | 0.700 | 0.794 | 0.629 | 0.744 | 0.429 |
| DINOv2 cues + vector | 408 | 57 | 92 | 334 | 0.833 | 0.79-0.87 | 0.816 | 0.877 | 0.784 | 0.846 | 0.666 |
| base (production without DINO) | 401 | 64 | 87 | 339 | 0.831 | 0.79-0.86 | 0.822 | 0.862 | 0.796 | 0.842 | 0.661 |
| base + DINOv2 cues (production) | 408 | 57 | 83 | 343 | 0.843 | 0.81-0.88 | 0.831 | 0.877 | 0.805 | 0.854 | 0.686 |
| base + DINOv2 cues + vector | 409 | 56 | 80 | 346 | 0.847 | 0.81-0.88 | 0.836 | 0.880 | 0.812 | 0.857 | 0.694 |
| DINOv3 cues | 389 | 76 | 172 | 254 | 0.722 | 0.67-0.77 | 0.693 | 0.837 | 0.596 | 0.758 | 0.448 |
| DINOv3 cues + vector | 413 | 52 | 88 | 338 | 0.843 | 0.80-0.88 | 0.824 | 0.888 | 0.793 | 0.855 | 0.686 |
| base + DINOv3 cues | 405 | 60 | 88 | 338 | 0.834 | 0.80-0.87 | 0.822 | 0.871 | 0.793 | 0.846 | 0.668 |
| base + DINOv3 cues + vector | 410 | 55 | 90 | 336 | 0.837 | 0.80-0.87 | 0.820 | 0.882 | 0.789 | 0.850 | 0.675 |
| DINOv2 + DINOv3 cues | 387 | 78 | 134 | 292 | 0.762 | 0.72-0.80 | 0.743 | 0.832 | 0.685 | 0.785 | 0.525 |
| DINOv2 + DINOv3 cues + vectors | 425 | 40 | 86 | 340 | 0.859 | 0.82-0.89 | 0.832 | 0.914 | 0.798 | 0.871 | 0.719 |
| base + DINOv2 + DINOv3 cues | 411 | 54 | 84 | 342 | 0.845 | 0.81-0.88 | 0.830 | 0.884 | 0.803 | 0.856 | 0.690 |
| base + DINOv2 + DINOv3 cues + vectors | 415 | 50 | 85 | 341 | 0.848 | 0.81-0.88 | 0.830 | 0.892 | 0.800 | 0.860 | 0.698 |
| always "flooded" | 465 | 0 | 426 | 0 | 0.522 | 0.44-0.60 | 0.522 | 1.000 | 0.000 | 0.686 | 0.000 |

## Track B, 891 roads, paired

| arm | against | accuracy difference | 95% CI | roads fixed | roads broken | McNemar p |
|---|---|---|---|---|---|---|
| DINOv3 cues | DINOv2 cues | +0.007 | -0.030 to +0.046 | 114 | 108 | 0.7373 |
| DINOv3 cues + vector | DINOv2 cues + vector | +0.010 | -0.020 to +0.040 | 57 | 48 | 0.4351 |
| base + DINOv3 cues | base + DINOv2 cues (production) | -0.009 | -0.024 to +0.005 | 13 | 21 | 0.2295 |
| base + DINOv3 cues + vector | base + DINOv2 cues + vector | -0.010 | -0.025 to +0.005 | 16 | 25 | 0.2110 |
| DINOv2 + DINOv3 cues | DINOv2 cues | +0.047 | +0.021 to +0.075 | 88 | 46 | 0.0004 |
| DINOv2 + DINOv3 cues + vectors | DINOv2 cues + vector | +0.026 | +0.002 to +0.049 | 51 | 28 | 0.0128 |
| base + DINOv2 + DINOv3 cues | base + DINOv2 cues (production) | +0.002 | -0.013 to +0.016 | 21 | 19 | 0.8746 |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv2 cues + vector | +0.001 | -0.013 to +0.015 | 20 | 19 | 1.0000 |
| DINOv3 cues | base + DINOv2 cues (production) | -0.121 | -0.160 to -0.083 | 62 | 170 | 0.0000 |
| DINOv3 cues + vector | base + DINOv2 cues (production) | +0.000 | -0.025 to +0.025 | 51 | 51 | 1.0000 |
| base + DINOv3 cues + vector | base + DINOv2 cues (production) | -0.006 | -0.023 to +0.012 | 26 | 31 | 0.5966 |
| DINOv2 + DINOv3 cues | base + DINOv2 cues (production) | -0.081 | -0.115 to -0.048 | 55 | 127 | 0.0000 |
| DINOv2 + DINOv3 cues + vectors | base + DINOv2 cues (production) | +0.016 | -0.006 to +0.037 | 54 | 40 | 0.1797 |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv2 cues (production) | +0.006 | -0.013 to +0.023 | 31 | 26 | 0.5966 |
| DINOv2 + DINOv3 cues | DINOv3 cues | +0.040 | +0.010 to +0.068 | 93 | 57 | 0.0041 |
| DINOv2 + DINOv3 cues + vectors | DINOv3 cues + vector | +0.016 | +0.002 to +0.030 | 25 | 11 | 0.0288 |
| base + DINOv2 + DINOv3 cues | base + DINOv3 cues | +0.011 | +0.001 to +0.022 | 18 | 8 | 0.0755 |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv3 cues + vector | +0.011 | +0.002 to +0.021 | 14 | 4 | 0.0309 |
| base + DINOv2 cues (production) | base (production without DINO) | +0.012 | +0.002 to +0.023 | 17 | 6 | 0.0347 |
| base + DINOv2 cues + vector | base (production without DINO) | +0.017 | +0.003 to +0.031 | 28 | 13 | 0.0275 |
| base + DINOv3 cues | base (production without DINO) | +0.003 | -0.011 to +0.018 | 22 | 19 | 0.7552 |
| base + DINOv3 cues + vector | base (production without DINO) | +0.007 | -0.012 to +0.026 | 35 | 29 | 0.5323 |
| base + DINOv2 + DINOv3 cues | base (production without DINO) | +0.015 | -0.001 to +0.030 | 31 | 18 | 0.0854 |
| base + DINOv2 + DINOv3 cues + vectors | base (production without DINO) | +0.018 | -0.002 to +0.038 | 43 | 27 | 0.0722 |

## Track B, 798 roads

| arm | TP | FN | FP | TN | accuracy | accuracy 95% CI | precision | recall | dry kept dry | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base (production without DINO) | 381 | 60 | 89 | 268 | 0.813 | 0.78-0.85 | 0.811 | 0.864 | 0.751 | 0.836 | 0.621 |
| base + DINOv2 cues (production) | 394 | 47 | 89 | 268 | 0.830 | 0.79-0.86 | 0.816 | 0.893 | 0.751 | 0.853 | 0.655 |
| base + DINOv2 cues + vector | 394 | 47 | 88 | 269 | 0.831 | 0.80-0.87 | 0.817 | 0.893 | 0.754 | 0.854 | 0.658 |
| base + DINOv3 cues | 394 | 47 | 91 | 266 | 0.827 | 0.79-0.86 | 0.812 | 0.893 | 0.745 | 0.851 | 0.650 |
| base + DINOv3 cues + vector | 395 | 46 | 90 | 267 | 0.830 | 0.79-0.87 | 0.814 | 0.896 | 0.748 | 0.853 | 0.655 |
| base + DINOv2 + DINOv3 cues | 394 | 47 | 88 | 269 | 0.831 | 0.79-0.87 | 0.817 | 0.893 | 0.754 | 0.854 | 0.658 |
| base + DINOv2 + DINOv3 cues + vectors | 399 | 42 | 89 | 268 | 0.836 | 0.80-0.87 | 0.818 | 0.905 | 0.751 | 0.859 | 0.669 |
| always "flooded" | 441 | 0 | 357 | 0 | 0.553 | 0.47-0.63 | 0.553 | 1.000 | 0.000 | 0.712 | 0.000 |

## Track B, 798 roads, paired

| arm | against | accuracy difference | 95% CI | roads fixed | roads broken | McNemar p |
|---|---|---|---|---|---|---|
| base + DINOv3 cues | base + DINOv2 cues (production) | -0.003 | -0.018 to +0.013 | 18 | 20 | 0.8714 |
| base + DINOv3 cues + vector | base + DINOv2 cues + vector | -0.001 | -0.018 to +0.016 | 25 | 26 | 1.0000 |
| base + DINOv2 + DINOv3 cues | base + DINOv2 cues (production) | +0.001 | -0.014 to +0.017 | 19 | 18 | 1.0000 |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv2 cues + vector | +0.005 | -0.011 to +0.022 | 23 | 19 | 0.6440 |
| base + DINOv3 cues + vector | base + DINOv2 cues (production) | +0.000 | -0.019 to +0.017 | 25 | 25 | 1.0000 |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv2 cues (production) | +0.006 | -0.012 to +0.024 | 28 | 23 | 0.5758 |
| base + DINOv2 + DINOv3 cues | base + DINOv3 cues | +0.004 | -0.005 to +0.013 | 9 | 6 | 0.6072 |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv3 cues + vector | +0.006 | -0.008 to +0.021 | 19 | 14 | 0.4869 |
| base + DINOv2 cues (production) | base (production without DINO) | +0.016 | +0.005 to +0.028 | 20 | 7 | 0.0192 |
| base + DINOv2 cues + vector | base (production without DINO) | +0.018 | -0.001 to +0.037 | 32 | 18 | 0.0649 |
| base + DINOv3 cues | base (production without DINO) | +0.014 | -0.003 to +0.031 | 31 | 20 | 0.1608 |
| base + DINOv3 cues + vector | base (production without DINO) | +0.016 | -0.004 to +0.036 | 38 | 25 | 0.1299 |
| base + DINOv2 + DINOv3 cues | base (production without DINO) | +0.018 | +0.000 to +0.035 | 34 | 20 | 0.0759 |
| base + DINOv2 + DINOv3 cues + vectors | base (production without DINO) | +0.023 | +0.003 to +0.043 | 41 | 23 | 0.0328 |

## DINOv3 single cues

| features | TP | FN | FP | TN | accuracy | accuracy 95% CI | MCC |
|---|---|---|---|---|---|---|---|
| dino3_change_pooled | 407 | 58 | 220 | 206 | 0.688 | 0.63-0.74 | 0.393 |
| dino3_change_mean | 402 | 63 | 216 | 210 | 0.687 | 0.63-0.74 | 0.387 |
| dino3_change_max | 399 | 66 | 256 | 170 | 0.639 | 0.58-0.69 | 0.291 |
| always "flooded" | 465 | 0 | 426 | 0 | 0.522 | 0.44-0.60 | 0.000 |

## Track A

| cut-off | cells called road | precision | recall | F1 | F1 95% CI | F1 vs classical (0.77) | 95% CI of the difference |
|---|---|---|---|---|---|---|---|
| classical (0.77) | 7321 | 0.506 | 0.514 | 0.510 | 0.442-0.581 | 0.000 | +0.000 to +0.000 |
| classical + DINOv2 (0.75) | 7580 | 0.696 | 0.732 | 0.713 | 0.651-0.772 | 0.203 | +0.159 to +0.248 |
| DINOv2 only (0.76) | 7777 | 0.658 | 0.710 | 0.683 | 0.620-0.745 | 0.173 | +0.117 to +0.228 |
| classical + DINOv3 (0.71) | 7368 | 0.738 | 0.755 | 0.747 | 0.690-0.802 | 0.237 | +0.194 to +0.284 |
| DINOv3 only (0.69) | 7660 | 0.711 | 0.756 | 0.733 | 0.672-0.793 | 0.223 | +0.173 to +0.275 |
| classical + DINOv2 + DINOv3 (0.70) | 7848 | 0.722 | 0.786 | 0.753 | 0.689-0.811 | 0.243 | +0.196 to +0.289 |
| DINOv2 + DINOv3 (0.72) | 7582 | 0.732 | 0.771 | 0.751 | 0.687-0.811 | 0.241 | +0.192 to +0.291 |

| arm | TP | FN | FP | TN |
|---|---|---|---|---|
| classical (0.77) | 3704 | 3501 | 3617 | 328063 |
| classical + DINOv2 (0.75) | 5274 | 1931 | 2306 | 329374 |
| DINOv2 only (0.76) | 5116 | 2089 | 2661 | 329019 |
| classical + DINOv3 (0.71) | 5441 | 1764 | 1927 | 329753 |
| DINOv3 only (0.69) | 5447 | 1758 | 2213 | 329467 |
| classical + DINOv2 + DINOv3 (0.70) | 5666 | 1539 | 2182 | 329498 |
| DINOv2 + DINOv3 (0.72) | 5552 | 1653 | 2030 | 329650 |

| arm | against | F1 | F1 difference | 95% CI of the difference |
|---|---|---|---|---|
| classical + DINOv3 (0.71) | classical + DINOv2 (0.75) | 0.747 | +0.033 | +0.014 to +0.057 |
| DINOv3 only (0.69) | DINOv2 only (0.76) | 0.733 | +0.050 | +0.021 to +0.082 |
| classical + DINOv2 + DINOv3 (0.70) | classical + DINOv2 (0.75) | 0.753 | +0.039 | +0.027 to +0.052 |
| DINOv2 + DINOv3 (0.72) | DINOv2 only (0.76) | 0.751 | +0.068 | +0.051 to +0.090 |
| classical + DINOv2 + DINOv3 (0.70) | classical + DINOv3 (0.71) | 0.753 | +0.006 | -0.010 to +0.021 |

{
 "times (s)": {
  "Track B road tokens, train": 5.3,
  "Track B road tokens, val": 0.0,
  "Track A cell basis (training tiles)": 0.0,
  "Track A cell features, train": 0.3,
  "Track A cell features, val": 0.4,
  "note": "Track B times from the first features run (features_trackB.log), stopped after Track B; the cell basis also built the float32 before-image trunk cache; the GPU was shared with another agent's job and ran about 3.5x slower than benchmarked",
  "road prior (training tiles)": 182.6,
  "Track A detector fits (all arms, s)": 5519.2,
  "Track B DINOv2 cues (891 roads)": 2.3,
  "Track B DINOv2 cues + vector (891 roads)": 5.1,
  "Track B base (production without DINO) (891 roads)": 2.7,
  "Track B base + DINOv2 cues (production) (891 roads)": 2.7,
  "Track B base + DINOv2 cues + vector (891 roads)": 5.0,
  "Track B DINOv3 cues (891 roads)": 2.1,
  "Track B DINOv3 cues + vector (891 roads)": 5.7,
  "Track B base + DINOv3 cues (891 roads)": 2.7,
  "Track B base + DINOv3 cues + vector (891 roads)": 6.0,
  "Track B DINOv2 + DINOv3 cues (891 roads)": 2.2,
  "Track B DINOv2 + DINOv3 cues + vectors (891 roads)": 7.8,
  "Track B base + DINOv2 + DINOv3 cues (891 roads)": 2.7,
  "Track B base + DINOv2 + DINOv3 cues + vectors (891 roads)": 7.8,
  "Track B base (production without DINO) (798 roads)": 2.2,
  "Track B base + DINOv2 cues (production) (798 roads)": 2.7,
  "Track B base + DINOv2 cues + vector (798 roads)": 5.3,
  "Track B base + DINOv3 cues (798 roads)": 2.9,
  "Track B base + DINOv3 cues + vector (798 roads)": 4.9,
  "Track B base + DINOv2 + DINOv3 cues (798 roads)": 2.9,
  "Track B base + DINOv2 + DINOv3 cues + vectors (798 roads)": 9.4,
  "pictures": 346.0,
  "this run total": 3134.1
 },
 "DINOv2 reproduction (now, logged)": {
  "DINOv2 cues": [
   0.715,
   0.715
  ],
  "DINOv2 cues + vector": [
   0.833,
   0.833
  ],
  "base (production without DINO)": [
   0.831,
   0.831
  ],
  "base + DINOv2 cues (production)": [
   0.843,
   0.843
  ],
  "base + DINOv2 cues + vector": [
   0.847,
   0.847
  ]
 },
 "data": {
  "train tiles": 186,
  "val tiles": 40,
  "roads (tile rule)": 891,
  "roads (production cloud rule)": 798,
  "training cells": 205581,
  "validation cells": 338885,
  "road share sampled / real": [
   0.2499744626205729,
   0.02206471425608241
  ]
 },
 "pictures": {
  "tile B": "2_15_48",
  "tile A": "0_14_7",
  "patch change, median / 99th percentile": {
   "DINOv2": [
    0.3700837790966034,
    0.8557600378990173
   ],
   "DINOv3": [
    0.4434961974620819,
    0.7607024312019348
   ]
  }
 }
}
