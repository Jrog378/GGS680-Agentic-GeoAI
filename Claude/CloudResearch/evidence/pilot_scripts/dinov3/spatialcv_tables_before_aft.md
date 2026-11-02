# Spatial CV of the DINOv3 benchmark: tables (generated)

## Track B frozen arms, 891 roads, spatial folds (seed 662)
| arm | TP | FN | FP | TN | accuracy | accuracy 95% CI | precision | recall | specificity | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DINOv2 cues | 371 | 94 | 162 | 264 | 0.713 | 0.652-0.775 | 0.696 | 0.798 | 0.620 | 0.743 | 0.425 |
| DINOv2 cues + vector | 403 | 62 | 112 | 314 | 0.805 | 0.757-0.851 | 0.783 | 0.867 | 0.737 | 0.822 | 0.611 |
| base (production without DINO) | 383 | 82 | 112 | 314 | 0.782 | 0.722-0.836 | 0.774 | 0.824 | 0.737 | 0.798 | 0.564 |
| base + DINOv2 cues (production) | 384 | 81 | 103 | 323 | 0.793 | 0.735-0.846 | 0.789 | 0.826 | 0.758 | 0.807 | 0.586 |
| base + DINOv2 cues + vector | 401 | 64 | 100 | 326 | 0.816 | 0.766-0.859 | 0.800 | 0.862 | 0.765 | 0.830 | 0.632 |
| DINOv3 cues | 382 | 83 | 171 | 255 | 0.715 | 0.650-0.780 | 0.691 | 0.822 | 0.599 | 0.750 | 0.432 |
| DINOv3 cues + vector | 419 | 46 | 105 | 321 | 0.831 | 0.777-0.882 | 0.800 | 0.901 | 0.754 | 0.847 | 0.664 |
| base + DINOv3 cues | 387 | 78 | 102 | 324 | 0.798 | 0.744-0.848 | 0.791 | 0.832 | 0.761 | 0.811 | 0.595 |
| base + DINOv3 cues + vector | 407 | 58 | 98 | 328 | 0.825 | 0.770-0.873 | 0.806 | 0.875 | 0.770 | 0.839 | 0.650 |
| DINOv2 + DINOv3 cues | 391 | 74 | 135 | 291 | 0.765 | 0.709-0.822 | 0.743 | 0.841 | 0.683 | 0.789 | 0.532 |
| DINOv2 + DINOv3 cues + vectors | 424 | 41 | 92 | 334 | 0.851 | 0.803-0.895 | 0.822 | 0.912 | 0.784 | 0.864 | 0.704 |
| base + DINOv2 + DINOv3 cues | 393 | 72 | 105 | 321 | 0.801 | 0.747-0.851 | 0.789 | 0.845 | 0.754 | 0.816 | 0.602 |
| base + DINOv2 + DINOv3 cues + vectors | 413 | 52 | 98 | 328 | 0.832 | 0.781-0.876 | 0.808 | 0.888 | 0.770 | 0.846 | 0.665 |
| always "flooded" | 465 | 0 | 426 | 0 | 0.522 | 0.381-0.647 | 0.522 | 1.000 | 0.000 | 0.686 | 0.000 |

| arm | against | difference | 95% CI | roads fixed | roads broken | McNemar p | verdict |
|---|---|---|---|---|---|---|---|
| DINOv3 cues | DINOv2 cues | 0.002 | -0.047 to +0.058 | 118 | 116 | 0.948 | no detectable difference |
| DINOv3 cues + vector | DINOv2 cues + vector | 0.026 | -0.016 to +0.069 | 76 | 53 | 0.052 | no detectable difference |
| base + DINOv3 cues | base + DINOv2 cues (production) | 0.004 | -0.009 to +0.021 | 21 | 17 | 0.627 | no detectable difference |
| base + DINOv3 cues + vector | base + DINOv2 cues + vector | 0.009 | -0.012 to +0.030 | 33 | 25 | 0.358 | no detectable difference |
| DINOv2 + DINOv3 cues | DINOv2 cues | 0.053 | +0.020 to +0.095 | 94 | 47 | 0.000 | beats |
| DINOv2 + DINOv3 cues + vectors | DINOv2 cues + vector | 0.046 | +0.013 to +0.083 | 66 | 25 | 0.000 | beats |
| base + DINOv2 + DINOv3 cues | base + DINOv2 cues (production) | 0.008 | -0.005 to +0.023 | 28 | 21 | 0.392 | no detectable difference |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv2 cues + vector | 0.016 | +0.001 to +0.031 | 29 | 15 | 0.049 | beats |
| DINOv3 cues | base + DINOv2 cues (production) | -0.079 | -0.133 to -0.020 | 93 | 163 | 0.000 | worse |
| DINOv3 cues + vector | base + DINOv2 cues (production) | 0.037 | -0.001 to +0.078 | 89 | 56 | 0.008 | no detectable difference |
| base + DINOv3 cues + vector | base + DINOv2 cues (production) | 0.031 | +0.010 to +0.055 | 50 | 22 | 0.001 | beats |
| DINOv2 + DINOv3 cues | base + DINOv2 cues (production) | -0.028 | -0.072 to +0.025 | 89 | 114 | 0.092 | no detectable difference |
| DINOv2 + DINOv3 cues + vectors | base + DINOv2 cues (production) | 0.057 | +0.023 to +0.099 | 95 | 44 | 0.000 | beats |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv2 cues (production) | 0.038 | +0.020 to +0.059 | 55 | 21 | 0.000 | beats |
| DINOv2 + DINOv3 cues | DINOv3 cues | 0.051 | +0.022 to +0.081 | 89 | 44 | 0.000 | beats |
| DINOv2 + DINOv3 cues + vectors | DINOv3 cues + vector | 0.020 | +0.002 to +0.041 | 32 | 14 | 0.011 | beats |
| base + DINOv2 + DINOv3 cues | base + DINOv3 cues | 0.003 | -0.006 to +0.013 | 18 | 15 | 0.728 | no detectable difference |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv3 cues + vector | 0.007 | -0.007 to +0.022 | 20 | 14 | 0.392 | no detectable difference |
| base + DINOv2 cues (production) | base (production without DINO) | 0.011 | -0.010 to +0.031 | 26 | 16 | 0.164 | no detectable difference |
| base + DINOv2 cues + vector | base (production without DINO) | 0.034 | +0.006 to +0.062 | 54 | 24 | 0.001 | beats |
| base + DINOv3 cues | base (production without DINO) | 0.016 | -0.003 to +0.035 | 36 | 22 | 0.087 | no detectable difference |
| base + DINOv3 cues + vector | base (production without DINO) | 0.043 | +0.019 to +0.069 | 57 | 19 | 0.000 | beats |
| base + DINOv2 + DINOv3 cues | base (production without DINO) | 0.019 | -0.002 to +0.041 | 44 | 27 | 0.057 | no detectable difference |
| base + DINOv2 + DINOv3 cues + vectors | base (production without DINO) | 0.049 | +0.023 to +0.077 | 71 | 27 | 0.000 | beats |
| DINOv3 cues | base + DINOv2 cues + vector | -0.101 | -0.152 to -0.044 | 70 | 160 | 0.000 | worse |
| DINOv3 cues + vector | base + DINOv2 cues + vector | 0.015 | -0.020 to +0.052 | 68 | 55 | 0.279 | no detectable difference |
| base + DINOv3 cues | base + DINOv2 cues + vector | -0.018 | -0.034 to -0.001 | 19 | 35 | 0.040 | worse |
| DINOv2 + DINOv3 cues | base + DINOv2 cues + vector | -0.051 | -0.089 to -0.004 | 66 | 111 | 0.001 | worse |
| DINOv2 + DINOv3 cues + vectors | base + DINOv2 cues + vector | 0.035 | +0.005 to +0.070 | 68 | 37 | 0.003 | beats |
| base + DINOv2 + DINOv3 cues | base + DINOv2 cues + vector | -0.015 | -0.030 to +0.002 | 16 | 29 | 0.072 | no detectable difference |

### Optimism (old tile folds minus spatial folds, 891 roads)
| arm | difference | 95% CI | roads fixed | roads broken | McNemar p |
|---|---|---|---|---|---|
| DINOv2 cues | 0.002 | -0.013 to +0.019 | 35 | 33 | 0.904 |
| DINOv2 cues + vector | 0.028 | +0.009 to +0.053 | 43 | 18 | 0.002 |
| base (production without DINO) | 0.048 | +0.023 to +0.079 | 61 | 18 | 0.000 |
| base + DINOv2 cues (production) | 0.049 | +0.026 to +0.080 | 54 | 10 | 0.000 |
| base + DINOv2 cues + vector | 0.031 | +0.011 to +0.058 | 43 | 15 | 0.000 |
| DINOv3 cues | 0.007 | -0.018 to +0.032 | 44 | 38 | 0.581 |
| DINOv3 cues + vector | 0.012 | -0.004 to +0.033 | 34 | 23 | 0.185 |
| base + DINOv3 cues | 0.036 | +0.018 to +0.060 | 46 | 14 | 0.000 |
| base + DINOv3 cues + vector | 0.012 | -0.006 to +0.039 | 34 | 23 | 0.185 |
| DINOv2 + DINOv3 cues | -0.003 | -0.022 to +0.013 | 32 | 35 | 0.807 |
| DINOv2 + DINOv3 cues + vectors | 0.008 | -0.007 to +0.026 | 26 | 19 | 0.371 |
| base + DINOv2 + DINOv3 cues | 0.044 | +0.026 to +0.067 | 50 | 11 | 0.000 |
| base + DINOv2 + DINOv3 cues + vectors | 0.017 | -0.004 to +0.044 | 36 | 21 | 0.063 |

## Track B frozen arms, 798 roads, spatial folds (seed 662)
| arm | TP | FN | FP | TN | accuracy | accuracy 95% CI | precision | recall | specificity | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base (production without DINO) | 373 | 68 | 102 | 255 | 0.787 | 0.731-0.838 | 0.785 | 0.846 | 0.714 | 0.814 | 0.567 |
| base + DINOv2 cues (production) | 378 | 63 | 103 | 254 | 0.792 | 0.733-0.845 | 0.786 | 0.857 | 0.711 | 0.820 | 0.578 |
| base + DINOv2 cues + vector | 388 | 53 | 106 | 251 | 0.801 | 0.747-0.849 | 0.785 | 0.880 | 0.703 | 0.830 | 0.597 |
| base + DINOv3 cues | 382 | 59 | 102 | 255 | 0.798 | 0.745-0.849 | 0.789 | 0.866 | 0.714 | 0.826 | 0.591 |
| base + DINOv3 cues + vector | 394 | 47 | 101 | 256 | 0.815 | 0.760-0.868 | 0.796 | 0.893 | 0.717 | 0.842 | 0.625 |
| base + DINOv2 + DINOv3 cues | 384 | 57 | 99 | 258 | 0.805 | 0.754-0.855 | 0.795 | 0.871 | 0.723 | 0.831 | 0.604 |
| base + DINOv2 + DINOv3 cues + vectors | 404 | 37 | 99 | 258 | 0.830 | 0.778-0.876 | 0.803 | 0.916 | 0.723 | 0.856 | 0.658 |
| always "flooded" | 441 | 0 | 357 | 0 | 0.553 | 0.407-0.672 | 0.553 | 1.000 | 0.000 | 0.712 | 0.000 |

| arm | against | difference | 95% CI | roads fixed | roads broken | McNemar p | verdict |
|---|---|---|---|---|---|---|---|
| base + DINOv3 cues | base + DINOv2 cues (production) | 0.006 | -0.009 to +0.025 | 22 | 17 | 0.522 | no detectable difference |
| base + DINOv3 cues + vector | base + DINOv2 cues + vector | 0.014 | -0.007 to +0.037 | 33 | 22 | 0.177 | no detectable difference |
| base + DINOv2 + DINOv3 cues | base + DINOv2 cues (production) | 0.013 | -0.003 to +0.034 | 28 | 18 | 0.184 | no detectable difference |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv2 cues + vector | 0.029 | +0.011 to +0.048 | 36 | 13 | 0.001 | beats |
| base + DINOv3 cues + vector | base + DINOv2 cues (production) | 0.023 | -0.004 to +0.055 | 43 | 25 | 0.038 | no detectable difference |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv2 cues (production) | 0.038 | +0.012 to +0.067 | 51 | 21 | 0.001 | beats |
| base + DINOv2 + DINOv3 cues | base + DINOv3 cues | 0.006 | -0.009 to +0.023 | 17 | 12 | 0.458 | no detectable difference |
| base + DINOv2 + DINOv3 cues + vectors | base + DINOv3 cues + vector | 0.015 | -0.006 to +0.036 | 25 | 13 | 0.073 | no detectable difference |
| base + DINOv2 cues (production) | base (production without DINO) | 0.005 | -0.011 to +0.020 | 22 | 18 | 0.636 | no detectable difference |
| base + DINOv2 cues + vector | base (production without DINO) | 0.014 | -0.003 to +0.035 | 36 | 25 | 0.200 | no detectable difference |
| base + DINOv3 cues | base (production without DINO) | 0.011 | -0.005 to +0.030 | 33 | 24 | 0.289 | no detectable difference |
| base + DINOv3 cues + vector | base (production without DINO) | 0.028 | +0.001 to +0.061 | 54 | 32 | 0.023 | beats |
| base + DINOv2 + DINOv3 cues | base (production without DINO) | 0.018 | -0.001 to +0.042 | 41 | 27 | 0.114 | no detectable difference |
| base + DINOv2 + DINOv3 cues + vectors | base (production without DINO) | 0.043 | +0.017 to +0.072 | 62 | 28 | 0.000 | beats |
| base + DINOv3 cues | base + DINOv2 cues + vector | -0.003 | -0.021 to +0.015 | 21 | 23 | 0.880 | no detectable difference |
| base + DINOv2 + DINOv3 cues | base + DINOv2 cues + vector | 0.004 | -0.012 to +0.021 | 23 | 20 | 0.761 | no detectable difference |

### Optimism (old tile folds minus spatial folds, 798 roads)
| arm | difference | 95% CI | roads fixed | roads broken | McNemar p |
|---|---|---|---|---|---|
| base (production without DINO) | 0.026 | +0.006 to +0.054 | 41 | 20 | 0.010 |
| base + DINOv2 cues (production) | 0.038 | +0.020 to +0.062 | 49 | 19 | 0.000 |
| base + DINOv2 cues + vector | 0.030 | +0.008 to +0.058 | 46 | 22 | 0.005 |
| base + DINOv3 cues | 0.029 | +0.008 to +0.055 | 43 | 20 | 0.005 |
| base + DINOv3 cues + vector | 0.015 | -0.001 to +0.033 | 33 | 21 | 0.134 |
| base + DINOv2 + DINOv3 cues | 0.026 | +0.006 to +0.049 | 39 | 18 | 0.008 |
| base + DINOv2 + DINOv3 cues + vectors | 0.006 | -0.017 to +0.031 | 30 | 25 | 0.590 |

## Track B trained-cue arms, 891 roads, spatial folds (seed 662)
| arm | TP | FN | FP | TN | accuracy | accuracy 95% CI | precision | recall | specificity | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base (production without DINO) | 383 | 82 | 112 | 314 | 0.782 | 0.722-0.836 | 0.774 | 0.824 | 0.737 | 0.798 | 0.564 |
| base + DINOv2 cues (production) | 384 | 81 | 103 | 323 | 0.793 | 0.735-0.846 | 0.789 | 0.826 | 0.758 | 0.807 | 0.586 |
| base + DINOv3 cues (frozen) | 387 | 78 | 102 | 324 | 0.798 | 0.744-0.848 | 0.791 | 0.832 | 0.761 | 0.811 | 0.595 |
| base + DINOv2 cues + DINOv3 head cues | 415 | 50 | 89 | 337 | 0.844 | 0.793-0.890 | 0.823 | 0.892 | 0.791 | 0.857 | 0.689 |
| base + DINOv3 head cues | 415 | 50 | 96 | 330 | 0.836 | 0.787-0.883 | 0.812 | 0.892 | 0.775 | 0.850 | 0.674 |
| DINOv2 cues | 371 | 94 | 162 | 264 | 0.713 | 0.652-0.775 | 0.696 | 0.798 | 0.620 | 0.743 | 0.425 |
| DINOv3 cues (frozen) | 382 | 83 | 171 | 255 | 0.715 | 0.650-0.780 | 0.691 | 0.822 | 0.599 | 0.750 | 0.432 |
| DINOv3 head cues | 406 | 59 | 104 | 322 | 0.817 | 0.762-0.870 | 0.796 | 0.873 | 0.756 | 0.833 | 0.635 |
| always "flooded" | 465 | 0 | 426 | 0 | 0.522 | 0.381-0.647 | 0.522 | 1.000 | 0.000 | 0.686 | 0.000 |

| arm | against | difference | 95% CI | roads fixed | roads broken | McNemar p | verdict |
|---|---|---|---|---|---|---|---|
| base + DINOv2 cues + DINOv3 head cues | base + DINOv2 cues (production) | 0.051 | +0.022 to +0.084 | 66 | 21 | 0.000 | beats |
| base + DINOv3 head cues | base + DINOv2 cues (production) | 0.043 | +0.015 to +0.077 | 67 | 29 | 0.000 | beats |
| base + DINOv3 head cues | base + DINOv3 cues (frozen) | 0.038 | +0.018 to +0.062 | 61 | 27 | 0.000 | beats |
| base + DINOv3 cues (frozen) | base + DINOv2 cues (production) | 0.004 | -0.009 to +0.021 | 21 | 17 | 0.627 | no detectable difference |
| DINOv3 head cues | DINOv3 cues (frozen) | 0.102 | +0.054 to +0.158 | 160 | 69 | 0.000 | beats |
| DINOv3 head cues | DINOv2 cues | 0.104 | +0.048 to +0.171 | 173 | 80 | 0.000 | beats |
| DINOv3 cues (frozen) | DINOv2 cues | 0.002 | -0.047 to +0.058 | 118 | 116 | 0.948 | no detectable difference |
| base + DINOv2 cues (production) | base (production without DINO) | 0.011 | -0.010 to +0.031 | 26 | 16 | 0.164 | no detectable difference |
| base + DINOv2 cues + DINOv3 head cues | base + DINOv2 cues + vector (best combo) | 0.028 | +0.003 to +0.058 | 47 | 22 | 0.004 | beats |
| base + DINOv3 head cues | base + DINOv2 cues + vector (best combo) | 0.020 | -0.006 to +0.050 | 48 | 30 | 0.054 | no detectable difference |
| DINOv3 head cues | base + DINOv2 cues + vector (best combo) | 0.001 | -0.044 to +0.052 | 88 | 87 | 1.000 | no detectable difference |

## Track B trained-cue arms, 798 roads, spatial folds (seed 662)
| arm | TP | FN | FP | TN | accuracy | accuracy 95% CI | precision | recall | specificity | F1 | MCC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base (production without DINO) | 373 | 68 | 102 | 255 | 0.787 | 0.731-0.838 | 0.785 | 0.846 | 0.714 | 0.814 | 0.567 |
| base + DINOv2 cues (production) | 378 | 63 | 103 | 254 | 0.792 | 0.733-0.845 | 0.786 | 0.857 | 0.711 | 0.820 | 0.578 |
| base + DINOv3 cues (frozen) | 382 | 59 | 102 | 255 | 0.798 | 0.745-0.849 | 0.789 | 0.866 | 0.714 | 0.826 | 0.591 |
| base + DINOv2 cues + DINOv3 head cues | 399 | 42 | 96 | 261 | 0.827 | 0.771-0.877 | 0.806 | 0.905 | 0.731 | 0.853 | 0.651 |
| base + DINOv3 head cues | 397 | 44 | 93 | 264 | 0.828 | 0.769-0.882 | 0.810 | 0.900 | 0.739 | 0.853 | 0.653 |
| DINOv2 cues | 361 | 80 | 171 | 186 | 0.685 | 0.623-0.749 | 0.679 | 0.819 | 0.521 | 0.742 | 0.358 |
| DINOv3 cues (frozen) | 383 | 58 | 154 | 203 | 0.734 | 0.672-0.794 | 0.713 | 0.868 | 0.569 | 0.783 | 0.463 |
| DINOv3 head cues | 393 | 48 | 102 | 255 | 0.812 | 0.764-0.860 | 0.794 | 0.891 | 0.714 | 0.840 | 0.620 |
| always "flooded" | 441 | 0 | 357 | 0 | 0.553 | 0.407-0.672 | 0.553 | 1.000 | 0.000 | 0.712 | 0.000 |

| arm | against | difference | 95% CI | roads fixed | roads broken | McNemar p | verdict |
|---|---|---|---|---|---|---|---|
| base + DINOv2 cues + DINOv3 head cues | base + DINOv2 cues (production) | 0.035 | +0.007 to +0.068 | 54 | 26 | 0.002 | beats |
| base + DINOv3 head cues | base + DINOv2 cues (production) | 0.036 | +0.002 to +0.073 | 54 | 25 | 0.001 | beats |
| base + DINOv3 head cues | base + DINOv3 cues (frozen) | 0.030 | +0.004 to +0.059 | 44 | 20 | 0.004 | beats |
| base + DINOv3 cues (frozen) | base + DINOv2 cues (production) | 0.006 | -0.009 to +0.025 | 22 | 17 | 0.522 | no detectable difference |
| DINOv3 head cues | DINOv3 cues (frozen) | 0.078 | +0.031 to +0.130 | 116 | 54 | 0.000 | beats |
| DINOv3 head cues | DINOv2 cues | 0.127 | +0.068 to +0.193 | 161 | 60 | 0.000 | beats |
| DINOv3 cues (frozen) | DINOv2 cues | 0.049 | +0.017 to +0.088 | 110 | 71 | 0.005 | beats |
| base + DINOv2 cues (production) | base (production without DINO) | 0.005 | -0.011 to +0.020 | 22 | 18 | 0.636 | no detectable difference |

## Track A, held-out validation-split cells (spatial folds)
| arm | precision | recall | F1 | F1 95% CI | F1 vs classical + DINOv2 (production), frozen | 95% CI of the difference | verdict |
|---|---|---|---|---|---|---|---|
| classical + DINOv2 (production), frozen | 0.701 | 0.718 | 0.709 | 0.639-0.776 | 0.000 | +0.000 to +0.000 | - |
| classical + DINOv3, frozen | 0.741 | 0.723 | 0.732 | 0.667-0.800 | 0.023 | +0.002 to +0.047 | beats |
| DINOv3 only, frozen | 0.713 | 0.731 | 0.722 | 0.654-0.792 | 0.013 | -0.015 to +0.044 | no detectable difference |
| DINOv2 only, frozen | 0.660 | 0.702 | 0.680 | 0.609-0.742 | -0.029 | -0.050 to -0.013 | worse |
| DINOv3 linear head on frozen tokens | 0.666 | 0.651 | 0.658 | 0.582-0.732 | -0.051 | -0.087 to -0.020 | worse |

## Track A, all held-out cells weighted to the real road share
| arm | precision | recall | F1 | F1 95% CI | F1 vs classical + DINOv2 (production), frozen | 95% CI of the difference | verdict |
|---|---|---|---|---|---|---|---|
| classical + DINOv2 (production), frozen | 0.688 | 0.676 | 0.682 | 0.648-0.716 | 0.000 | +0.000 to +0.000 | - |
| classical + DINOv3, frozen | 0.741 | 0.695 | 0.717 | 0.683-0.749 | 0.035 | +0.021 to +0.051 | beats |
| DINOv3 only, frozen | 0.716 | 0.688 | 0.702 | 0.671-0.733 | 0.020 | +0.001 to +0.040 | beats |
| DINOv2 only, frozen | 0.664 | 0.646 | 0.655 | 0.623-0.687 | -0.027 | -0.038 to -0.017 | worse |
| DINOv3 linear head on frozen tokens | 0.683 | 0.607 | 0.643 | 0.605-0.678 | -0.039 | -0.062 to -0.017 | worse |

## Track A pairs
| scope | arm | against | F1 | F1 difference | 95% CI | verdict |
|---|---|---|---|---|---|---|
| val cells | DINOv3 only, frozen | DINOv2 only, frozen | 0.722 | 0.042 | +0.010 to +0.082 | beats |
| all cells (weighted) | DINOv3 only, frozen | DINOv2 only, frozen | 0.702 | 0.047 | +0.028 to +0.067 | beats |
| val cells | DINOv3 linear head on frozen tokens | DINOv3 only, frozen | 0.658 | -0.064 | -0.098 to -0.034 | worse |
| all cells (weighted) | DINOv3 linear head on frozen tokens | DINOv3 only, frozen | 0.643 | -0.059 | -0.082 to -0.039 | worse |
