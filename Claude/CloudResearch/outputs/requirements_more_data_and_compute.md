# What more data and compute would help (for Justin to review)

Written 2026-10-26 by Claude, overnight, after the DINOv3 benchmark and fine-tuning (`evidence/11_dinov3_baseline.md`). Nothing
here has been downloaded or set up. Every item marked **needs your OK** waits for you.

## 1. Where our data runs out
All our numbers come from **one event in one place**: Hurricane Ida, Louisiana-East, Maxar 0.5 m, greyscale. We have
226 development tiles: 186 training and 40 validation.

| Limit | Number | Why it matters |
|---|---|---|
| Roads we can score | 1,037 roads in all; 891 on cloud-free tiles; 798 that the cloud rule assesses | Every flood test runs on these few hundred roads. Gains of 1-2 points are not significant (DINOv3 in place of DINOv2: -0.9 points, p = 0.23). |
| Validation roads (fine-tuned models are scored here only) | 124 roads on 36 tiles (tile rule); 104 on 34 tiles (cloud rule) | Tonight a 5.7-point gain (8 roads fixed, 1 broken) was only just significant, and its interval touched 0. Smaller gains cannot be told from noise. |
| Spatial independence of validation | 87 of the 124 (cloud rule: 77 of 104) validation roads are OSM ways that continue from a training tile, with the same flooded label | The fine-tuned DINOv3 flood gains (+5.7 to +9.6 points) sit almost entirely on these roads. We cannot yet say whether they hold in a new place. |
| Trusted flooded roads under thin cloud | **24** (on 39 tiles) | Every cloud result rests on them. For example, de-hazing found 3 more of the 24, which is not significant. |
| Flood labels under cloud | Only "flooded = yes" can be trusted. "No" never occurs in the label files, so a road hidden by cloud reads as dry. | Under cloud we cannot score dry roads, so false alarms cannot be counted there. |
| Cloud on the before image | **None** in Louisiana-East | We cannot test the before-date cloud handling (`07_cloud_gate_either_date.md`); the test gate misfires on 29 clear tiles. |
| Events, sensors, seasons | 1 event, 1 sensor, late summer, Gulf coast | We cannot show the pipeline adapts to other hazards, sensors or cloud (your universality rule). |
| Fine-tuning labels (Track B) | About 690 training roads give the flood targets; the pixels of one road all share its label | The fine-tuned flood head effectively learns from hundreds of examples, not millions of pixels. |

## 2. Data that could help (each one **needs your OK** to download; sizes and licences to confirm on the source page)
| Dataset | What it has | Source | Licence (to confirm) | Rough size | What it would fix |
|---|---|---|---|---|---|
| SpaceNet 8 Germany and Louisiana-West | The same task and labels | already on disk, **sealed** | CC BY-SA 4.0 | already here | The final test. Keep sealed unless you decide otherwise. |
| xBD / xView2 (Gupta et al. 2019) | Pre / post Maxar pairs for 19 disasters, several of them floods and hurricanes (Harvey, Florence, Michael, Midwest 2019, Nepal 2017); building damage labels, **no road labels** | xview2.org | CC BY-NC-SA 4.0 | tens of GB | More events and seasons for Track A, using OSM road lines as labels, and a check that the change cues transfer. No per-road flood labels. |
| FloodNet (Rahnemoonfar et al. 2021) | Post-Harvey drone images with "road flooded" / "road not flooded" classes | the FloodNet challenge page | to confirm | about 10 GB (to confirm) | Labelled flooded roads, but from a drone at centimetre scale: a different sensor and resolution. |
| Sen1Floods11 (Bonafilia et al. 2020) | Hand-labelled flood water for 11 events, Sentinel-1 SAR and Sentinel-2 | Cloud to Street / GitHub | CC BY 4.0 | about 14 GB | Flood water under cloud from SAR, at 10 m. Too coarse for single roads; useful for a water-under-cloud check. |
| CloudSEN12 (Aybar et al. 2022) | Expert cloud and thin-cloud masks, Sentinel-2 | Scientific Data / Hugging Face | CC BY 4.0 | large; subsets available | More cloud labels, including thin cloud, at 10 m. Complements HRC_WHU. |
| Maxar Open Data + Copernicus EMS + OSM | Event imagery (Maxar Open Data, e.g. recent hurricanes and floods), analyst-drawn flood extents (Copernicus EMS rapid mapping) and OSM roads | Maxar Open Data Program; emergency.copernicus.eu; OSM | CC BY-NC 4.0; Copernicus EMS attribution; ODbL | about 10-50 GB per event | Per-road flood labels for new events. **Your decision:** the labels would be derived (road intersected with a flood polygon), not shipped per road. That may conflict with the "published labels, unmodified" rule. |

**What would help most:**
1. **A spatially independent validation set, which needs no download.** Re-split Louisiana-East by area, for
   example by before scene: region 0 against region 2. Or hold out blocks of neighbouring tiles, so that no validation
   road continues from a training tile. This changes the logged split, so it is your decision. It is the cheapest
   way to check tonight's fine-tuned gains.
2. **A second event with per-road flood labels at VHR.** I know of no other open set like SpaceNet 8. The most likely
   path is the last row of the table, if you accept derived labels. Otherwise xBD gives more events for road
   finding.

## 3. Compute limits hit tonight
- **Hardware:** an Apple M2 with 16 GB unified memory, and its GPU (MPS) shared with the other agents.
- **Speed:** DINOv3 ViT-L ran 0.8 s per 688 x 608 window when alone, but about 2.7 s while the GPU was shared or
  throttled. Swap reached 6 GB of 7.
- **What that forced in fine-tuning:**
  - only the last 2 of the 24 blocks trained, on cached frozen features;
  - one window per tile per epoch;
  - no image augmentation;
  - one fixed learning rate, with no search and one seed.

  Once the GPU was free, the 5 cross-fit folds fitted: the whole fine-tuning run took 94 minutes. Full fine-tuning,
  LoRA on every block, augmentation, a learning-rate search and several seeds were out of reach.
- **CPU:** each road-detector random forest (300 trees, 205,581 training cells) took 10-20 minutes per arm under the
  shared CPU load.
- **Disk:** 13 GB free at the end. The DINOv3 trunk cache and checkpoints use 8.5 GB
  (`~/Masters/models/finetuned/dinov3_sat493m/`). The trunk cache (7.8 GB) can be deleted and rebuilt in about
  an hour, if you want the space; I have not deleted anything.
- **What would lift this:** a few hours on one rented data-centre GPU (for example 40-80 GB). That would allow full
  or LoRA fine-tuning with augmentation, 5-fold cross-fitting and several seeds. **Needs your OK** (an account and
  cost).

## 4. Decisions only you can make
1. **Re-split Louisiana-East spatially** (by area or blocks of tiles) for a development check of the fine-tuned
   DINOv3 gains? The logged split fingerprint would change.
2. Download any dataset in section 2? Which ones?
3. Are derived per-road flood labels (flood polygon x OSM road) acceptable, or do they break the "published labels,
   unmodified" rule?
4. Keep SpaceNet 8 Germany and Louisiana-West sealed until the final test? (Assumed yes.)
5. Licences:
   - DINOv3 stays a research benchmark under Meta's DINOv3 License, as you said.
   - Any fine-tuned DINOv3 weights are research-only too: they derive from DINOv3 and were trained on CC BY-SA
     SpaceNet 8.
   - OK to keep them only in `~/Masters/models/finetuned/`?
6. Rent a cloud GPU for a proper fine-tuning run? If yes, which provider and budget?
