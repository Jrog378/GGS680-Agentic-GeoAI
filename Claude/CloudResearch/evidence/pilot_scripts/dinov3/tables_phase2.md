## Track B, tile rule: {'train': 767, 'validation': 124, 'validation tiles': 36}

| arm | TP | FN | FP | TN | accuracy | accuracy 95% CI | precision | recall | dry kept dry | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base (production without DINO) | 55 | 8 | 11 | 50 | 0.847 | 0.79-0.91 | 0.833 | 0.873 | 0.820 | 0.853 | 0.694 |
| base + DINOv2 cues (production) | 55 | 8 | 11 | 50 | 0.847 | 0.77-0.92 | 0.833 | 0.873 | 0.820 | 0.853 | 0.694 |
| base + DINOv3 cues (frozen) | 54 | 9 | 11 | 50 | 0.839 | 0.76-0.92 | 0.831 | 0.857 | 0.820 | 0.844 | 0.678 |
| base + DINOv2 cues + DINOv3 head cues | 58 | 5 | 8 | 53 | 0.895 | 0.82-0.97 | 0.879 | 0.921 | 0.869 | 0.899 | 0.791 |
| base + DINOv2 cues + DINOv3 fine-tuned cues | 60 | 3 | 9 | 52 | 0.903 | 0.84-0.96 | 0.870 | 0.952 | 0.852 | 0.909 | 0.810 |
| base + DINOv3 head cues | 57 | 6 | 7 | 54 | 0.895 | 0.83-0.96 | 0.891 | 0.905 | 0.885 | 0.898 | 0.790 |
| base + DINOv3 fine-tuned cues | 58 | 5 | 9 | 52 | 0.887 | 0.83-0.95 | 0.866 | 0.921 | 0.852 | 0.892 | 0.776 |
| DINOv2 cues | 47 | 16 | 15 | 46 | 0.750 | 0.64-0.86 | 0.758 | 0.746 | 0.754 | 0.752 | 0.500 |
| DINOv3 cues (frozen) | 51 | 12 | 26 | 35 | 0.694 | 0.60-0.79 | 0.662 | 0.810 | 0.574 | 0.729 | 0.395 |
| DINOv3 head cues | 56 | 7 | 9 | 52 | 0.871 | 0.80-0.94 | 0.862 | 0.889 | 0.852 | 0.875 | 0.742 |
| DINOv3 fine-tuned cues | 55 | 8 | 10 | 51 | 0.855 | 0.79-0.92 | 0.846 | 0.873 | 0.836 | 0.859 | 0.710 |
| always "flooded" | 63 | 0 | 61 | 0 | 0.508 | 0.33-0.65 | 0.508 | 1.000 | 0.000 | 0.674 | 0.000 |

| arm | against | accuracy difference | 95% CI | roads fixed | roads broken | McNemar p |
|---|---|---|---|---|---|---|
| base + DINOv2 cues + DINOv3 fine-tuned cues | base + DINOv2 cues (production) | +0.057 | +0.000 to +0.125 | 8 | 1 | 0.0391 |
| base + DINOv2 cues + DINOv3 head cues | base + DINOv2 cues (production) | +0.048 | -0.018 to +0.132 | 8 | 2 | 0.1094 |
| base + DINOv3 fine-tuned cues | base + DINOv2 cues (production) | +0.040 | -0.018 to +0.113 | 6 | 1 | 0.1250 |
| base + DINOv3 fine-tuned cues | base + DINOv3 cues (frozen) | +0.048 | -0.031 to +0.131 | 9 | 3 | 0.1460 |
| base + DINOv3 head cues | base + DINOv3 cues (frozen) | +0.057 | +0.000 to +0.131 | 10 | 3 | 0.0923 |
| base + DINOv3 cues (frozen) | base + DINOv2 cues (production) | -0.008 | -0.038 to +0.031 | 3 | 4 | 1.0000 |
| base + DINOv2 cues + DINOv3 fine-tuned cues | base + DINOv2 cues + DINOv3 head cues | +0.008 | -0.045 to +0.056 | 4 | 3 | 1.0000 |
| DINOv3 fine-tuned cues | DINOv2 cues | +0.105 | +0.013 to +0.202 | 21 | 8 | 0.0241 |
| DINOv3 fine-tuned cues | DINOv3 cues (frozen) | +0.161 | +0.062 to +0.269 | 29 | 9 | 0.0017 |
| DINOv3 head cues | DINOv3 cues (frozen) | +0.177 | +0.083 to +0.281 | 32 | 10 | 0.0009 |
| DINOv3 cues (frozen) | DINOv2 cues | -0.057 | -0.186 to +0.070 | 20 | 27 | 0.3817 |

## Track B, production cloud rule: {'train': 694, 'validation': 104, 'validation tiles': 34}

| arm | TP | FN | FP | TN | accuracy | accuracy 95% CI | precision | recall | dry kept dry | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base (production without DINO) | 50 | 6 | 15 | 33 | 0.798 | 0.71-0.87 | 0.769 | 0.893 | 0.688 | 0.826 | 0.598 |
| base + DINOv2 cues (production) | 52 | 4 | 15 | 33 | 0.817 | 0.72-0.89 | 0.776 | 0.929 | 0.688 | 0.846 | 0.642 |
| base + DINOv3 cues (frozen) | 50 | 6 | 13 | 35 | 0.817 | 0.72-0.90 | 0.794 | 0.893 | 0.729 | 0.840 | 0.635 |
| base + DINOv2 cues + DINOv3 head cues | 54 | 2 | 8 | 40 | 0.904 | 0.83-0.97 | 0.871 | 0.964 | 0.833 | 0.915 | 0.810 |
| base + DINOv2 cues + DINOv3 fine-tuned cues | 55 | 1 | 10 | 38 | 0.894 | 0.82-0.96 | 0.846 | 0.982 | 0.792 | 0.909 | 0.797 |
| base + DINOv3 head cues | 54 | 2 | 10 | 38 | 0.885 | 0.81-0.96 | 0.844 | 0.964 | 0.792 | 0.900 | 0.775 |
| base + DINOv3 fine-tuned cues | 55 | 1 | 8 | 40 | 0.913 | 0.85-0.97 | 0.873 | 0.982 | 0.833 | 0.924 | 0.832 |
| DINOv2 cues | 44 | 12 | 21 | 27 | 0.683 | 0.59-0.78 | 0.677 | 0.786 | 0.562 | 0.727 | 0.359 |
| DINOv3 cues (frozen) | 44 | 12 | 18 | 30 | 0.712 | 0.61-0.81 | 0.710 | 0.786 | 0.625 | 0.746 | 0.417 |
| DINOv3 head cues | 49 | 7 | 7 | 41 | 0.865 | 0.81-0.93 | 0.875 | 0.875 | 0.854 | 0.875 | 0.729 |
| DINOv3 fine-tuned cues | 52 | 4 | 10 | 38 | 0.865 | 0.81-0.93 | 0.839 | 0.929 | 0.792 | 0.881 | 0.732 |
| always "flooded" | 56 | 0 | 48 | 0 | 0.538 | 0.36-0.69 | 0.538 | 1.000 | 0.000 | 0.700 | 0.000 |

| arm | against | accuracy difference | 95% CI | roads fixed | roads broken | McNemar p |
|---|---|---|---|---|---|---|
| base + DINOv2 cues + DINOv3 fine-tuned cues | base + DINOv2 cues (production) | +0.077 | +0.000 to +0.179 | 10 | 2 | 0.0386 |
| base + DINOv2 cues + DINOv3 head cues | base + DINOv2 cues (production) | +0.086 | +0.000 to +0.194 | 11 | 2 | 0.0225 |
| base + DINOv3 fine-tuned cues | base + DINOv2 cues (production) | +0.096 | +0.028 to +0.188 | 10 | 0 | 0.0020 |
| base + DINOv3 fine-tuned cues | base + DINOv3 cues (frozen) | +0.096 | +0.017 to +0.185 | 11 | 1 | 0.0063 |
| base + DINOv3 head cues | base + DINOv3 cues (frozen) | +0.067 | -0.019 to +0.169 | 11 | 4 | 0.1185 |
| base + DINOv3 cues (frozen) | base + DINOv2 cues (production) | +0.000 | -0.039 to +0.058 | 3 | 3 | 1.0000 |
| base + DINOv2 cues + DINOv3 fine-tuned cues | base + DINOv2 cues + DINOv3 head cues | -0.010 | -0.045 to +0.020 | 1 | 2 | 1.0000 |
| DINOv3 fine-tuned cues | DINOv2 cues | +0.183 | +0.080 to +0.300 | 27 | 8 | 0.0019 |
| DINOv3 fine-tuned cues | DINOv3 cues (frozen) | +0.154 | +0.055 to +0.266 | 21 | 5 | 0.0025 |
| DINOv3 head cues | DINOv3 cues (frozen) | +0.154 | +0.048 to +0.267 | 23 | 7 | 0.0052 |
| DINOv3 cues (frozen) | DINOv2 cues | +0.029 | -0.049 to +0.123 | 17 | 14 | 0.7201 |

## Track A

| cut-off | cells called road | precision | recall | F1 | F1 95% CI | F1 vs classical (0.77) | 95% CI of the difference |
|---|---|---|---|---|---|---|---|
| classical (0.77) | 7321 | 0.506 | 0.514 | 0.510 | 0.442-0.581 | 0.000 | +0.000 to +0.000 |
| classical + DINOv2 (0.75) | 7580 | 0.696 | 0.732 | 0.713 | 0.651-0.772 | 0.203 | +0.159 to +0.248 |
| DINOv2 only (0.76) | 7777 | 0.658 | 0.710 | 0.683 | 0.620-0.745 | 0.173 | +0.117 to +0.228 |
| classical + DINOv3 (0.71) | 7368 | 0.738 | 0.755 | 0.747 | 0.690-0.802 | 0.237 | +0.194 to +0.284 |
| DINOv3 only (0.69) | 7660 | 0.711 | 0.756 | 0.733 | 0.672-0.793 | 0.223 | +0.173 to +0.275 |
| DINOv3 linear head on frozen tokens (0.25) | 8000 | 0.648 | 0.719 | 0.681 | 0.617-0.746 | 0.171 | +0.112 to +0.228 |
| DINOv3 fine-tuned (last 2 blocks + head) (0.46) | 7491 | 0.766 | 0.796 | 0.780 | 0.722-0.836 | 0.271 | +0.216 to +0.322 |

| arm | TP | FN | FP | TN |
|---|---|---|---|---|
| classical (0.77) | 3704 | 3501 | 3617 | 328063 |
| classical + DINOv2 (0.75) | 5274 | 1931 | 2306 | 329374 |
| DINOv2 only (0.76) | 5116 | 2089 | 2661 | 329019 |
| classical + DINOv3 (0.71) | 5441 | 1764 | 1927 | 329753 |
| DINOv3 only (0.69) | 5447 | 1758 | 2213 | 329467 |
| DINOv3 linear head on frozen tokens (0.25) | 5180 | 2025 | 2820 | 328860 |
| DINOv3 fine-tuned (last 2 blocks + head) (0.46) | 5735 | 1470 | 1756 | 329924 |

| arm | against | F1 | F1 difference | 95% CI of the difference |
|---|---|---|---|---|
| DINOv3 fine-tuned (last 2 blocks + head) (0.46) | classical + DINOv2 (0.75) | 0.780 | +0.067 | +0.023 to +0.109 |
| DINOv3 fine-tuned (last 2 blocks + head) (0.46) | DINOv2 only (0.76) | 0.780 | +0.098 | +0.051 to +0.141 |
| DINOv3 fine-tuned (last 2 blocks + head) (0.46) | DINOv3 only (0.69) | 0.780 | +0.048 | -0.001 to +0.088 |
| DINOv3 fine-tuned (last 2 blocks + head) (0.46) | classical + DINOv3 (0.71) | 0.780 | +0.034 | -0.013 to +0.069 |
| DINOv3 fine-tuned (last 2 blocks + head) (0.46) | DINOv3 linear head on frozen tokens (0.25) | 0.780 | +0.099 | +0.056 to +0.137 |
| DINOv3 linear head on frozen tokens (0.25) | DINOv3 only (0.69) | 0.681 | -0.052 | -0.082 to -0.028 |
| DINOv3 linear head on frozen tokens (0.25) | classical + DINOv2 (0.75) | 0.681 | -0.032 | -0.060 to -0.006 |

{
 "times (s)": {
  "trunk cache (s)": 12.4,
  "trunk reproduction cosine (min)": 0.9999998807907104,
  "A-head training (s)": 473.0,
  "A-ft training (s)": 1632.3,
  "B-head strip tokens (s)": 185.7,
  "B-head training + cues (s)": 7.7,
  "B-ft training + cues (s)": 2888.5,
  "pictures (s)": 29.9,
  "total": 5662.3
 },
 "chosen": {
  "A cut-offs (inner validation)": {
   "A-head": 0.25,
   "A-ft": 0.46
  },
  "B-head epochs": 1,
  "B-ft epochs": 3,
  "B-ft folds": 5
 },
 "data": {
  "inner fit tiles": 148,
  "inner validation tiles": 38,
  "validation tiles": 40,
  "Track A labelled training cells": 15899866,
  "Track B target strip cells": 413132,
  "Track B target roads": 694
 },
 "pictures": {
  "tile B": "2_15_48",
  "tile A": "0_14_7"
 }
}
A-head [(1, 0.3068, 0.1605), (2, 0.1142, 0.0972), (3, 0.0813, 0.074), (4, 0.0691, 0.0627), (5, 0.0619, 0.0561), (6, 0.0545, 0.0516), (7, 0.055, 0.0486), (8, 0.0502, 0.0465), (9, 0.0509, 0.0448), (10, 0.0457, 0.0432), (11, 0.0372, 0.0419), (12, 0.0359, 0.0408)]
A-ft [(1, 0.1947, 0.0518), (2, 0.0465, 0.0399), (3, 0.0382, 0.0357), (4, 0.0359, 0.0356), (5, 0.0335, 0.0341), (6, 0.0294, 0.0342), (7, 0.0323, 0.0289), (8, 0.0283, 0.0291), (9, 0.0298, 0.0285), (10, 0.027, 0.0261), (11, 0.0203, 0.0263), (12, 0.0193, 0.0259), (13, 0.0201, 0.0276), (14, 0.0229, 0.0256), (15, 0.0196, 0.0259), (16, 0.0233, 0.0276), (17, 0.0205, 0.0265), (18, 0.0204, 0.0255), (19, 0.019, 0.0255), (20, 0.0223, 0.0267)]
B-head inner [(1, 0.2187, 0.2379), (2, 0.0871, 0.2793), (3, 0.0544, 0.2953), (4, 0.0429, 0.3465)]
B-head fold 0 [(1, 0.2068, nan)]
B-head fold 1 [(1, 0.1976, nan)]
B-head fold 2 [(1, 0.2038, nan)]
B-head fold 3 [(1, 0.211, nan)]
B-head fold 4 [(1, 0.2088, nan)]
B-ft inner [(1, 0.4671, 0.3556), (2, 0.5008, 0.3276), (3, 0.4288, 0.2735), (4, 0.349, 0.3509), (5, 0.2981, 0.3029), (6, 0.2516, 0.3459)]
B-ft fold 0 [(1, 0.4532, nan), (2, 0.2943, nan), (3, 0.3312, nan)]
B-ft fold 1 [(1, 0.4755, nan), (2, 0.2096, nan), (3, 0.3509, nan)]
B-ft fold 2 [(1, 0.4956, nan), (2, 0.3645, nan), (3, 0.2869, nan)]
B-ft fold 3 [(1, 0.4753, nan), (2, 0.2572, nan), (3, 0.346, nan)]
B-ft fold 4 [(1, 0.4097, nan), (2, 0.3379, nan), (3, 0.3411, nan)]
