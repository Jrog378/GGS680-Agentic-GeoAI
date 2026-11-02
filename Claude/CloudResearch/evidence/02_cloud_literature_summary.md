# Literature on cloud handling: summary for the research-question agents

Condensed from two project notes written 2026-10-23: `ProjectBranch/Literature/notes/clouds.md` (papers on disk) and `clouds_review_web.md` (open web pages). How deeply each source was read is in those notes; abstract-only reads are marked there. Citation rule in the project: journals with a JIF above 4 or company-led papers; others are method attributions. Our own reading and inference are marked 'My read'.

## 1. Summary: the most useful findings

1. **Flood datasets keep "can we see it?" separate from "is it flooded?".**
   - WorldFloods v1 adds cloud as a third output class (land, water, cloud), and its cloud labels were made automatically with s2cloudless (Mateo-Garcia et al. 2021).
   - WorldFloods v2 splits this into two independent binary masks, clear/cloud and land/water, so water can be called under thin cloud. Scores leave out only invalid pixels and bright opaque cloud. Scenes with much thin cloud go to human review (Portalés-Julià et al. 2023).
   - My read: this is the pattern for the roads: a per-road *visible* output and a separate *flooded* output, with "cannot assess" decided by the first.
2. **SpaceNet 8's "yes or missing" flood labels are a positive-unlabeled (PU) problem under cloud.**
   - PU learning has a remote-sensing precedent in TGRS (Li, Guo & Elkan 2011) and one in damage mapping (Xia, Yokoya & Adriano 2021; workshop paper, already excluded in the project).
   - The cheapest fix also matches what WorldFloods v2 and AnyTime-CD do: keep cloudy "missing" labels out of the negatives in the *training loss only*. Because the scored roads do not change, the stage rule can decide that arm.
3. **The clear before image can serve as a clear-sky reference.**
   - Hagolle et al. (2010, RSE; FORMOSAT-2 at 8 m and others) flag cloud from a per-pixel jump in blue reflectance, together with a test of how linearly correlated pixel neighbourhoods are between successive images. That is abstract-level, from a catalogue snippet.
   - My read: both tests work on one grey band. The correlation test is what separates thin haze from opaque cloud: under haze the ground pattern survives, under opaque cloud it does not. Because the test is relative to the before image, it should not fire on bright calm water the way the absolute dark channel did on the before images.
4. **For selective de-hazing on VHR, the closest published match is Makarau et al. (2014, TGRS; DLR).**
   - It builds a haze-thickness map for uneven haze by extending dark-object subtraction locally, and was tested on WorldView-2 (abstract).
   - Its stated limit is scenes with uniform, highly reflective land cover.
   - It is a better fit than haze-lines (Berman et al. 2020, which needs RGB colour clusters) or DehazeFormer (RGB; its own README warns that models trained on synthetic haze may fail on real haze).
5. **There is one human-labelled cloud reference that reaches 0.5 m: HRC_WHU** (Li et al. 2019, ISPRS JPRS).
   - 150 Google Earth RGB images at 0.5–15 m, cloud outlined by experts. Thin cloud counts as cloud only where the ground cannot be seen clearly. No shadows are labelled.
   - About 115 MB as a mirror zip. The official licence is academic use only.
   - Cloud-Adapter (Zou et al. 2025, TGRS) adapts a **frozen DINOv2-L** with about 0.6% extra parameters and reaches 89.05 mIoU on it, against 83.44 for the best baseline. It did not test across datasets.
6. **Matching shadows to clouds by geometry needs the cloud in view.**
   - Fmask, SPARCS and Le Hégarat-Mascle & André (2009) all pair a shadow with its cloud through sun and view geometry.
   - HRC_WHU's authors did not label shadows at all, because shadows were rare and hard to outline in high-resolution images.
   - My read: at 0.5 m, a cumulus shadow can fall outside the tile, as the main project found (K4, C3). A two-date test is the realistic substitute: a shadow darkens the road and keeps its texture, floodwater replaces it. This is untested.
7. **VLMs are fragile under cloud** (all academic preprints or workshop papers, so method attributions):
   - prompting CLIPSeg to segment cloud failed: every one of 60 prompts scored below the 0.255 mIoU zero-shot baseline (Kethavath & Hu 2026);
   - cloud and fog perturbations "significantly impair" remote-sensing MLLMs (RemoteShield 2026);
   - cloud-like overlays injected weather hallucinations into remote-sensing RAG answers (CloudWeb 2026).
   - My read: this supports the project role. Gemma describes visibility; the mask decides.
8. **Reporting abstention.**
   - Geifman & El-Yaniv (2017) build a selective classifier at a risk level the user sets. The project already lists `whitehead2022reliable` (borderline) for risk–coverage curves and `wen2025know` (TACL, kept) for abstention.
   - I found **no remote-sensing paper that reports risk–coverage curves for cloud abstention**. The only remote-sensing reject-option paper that surfaced is an IGARSS paper (metadata only). The project can fill this gap, using Olofsson et al. (2014, on disk) for reporting the cannot-assess share.

---

## 3. Open datasets with cloud labels

Ordered: VHR RGB first, then Gaofen, then Sentinel-2/Landsat, then flood datasets with a cloud or invalid class. Sizes are from the official page where it gives one; otherwise from a mirror, marked as such. "Account?" says what the page states; I tested no download.

| Dataset | Paper and venue (rule) | What is labelled, and who labelled it | Resolution, bands, count | Licence | Total size (small subset) | Download URL | Account? |
|---|---|---|---|---|---|---|---|
| **HRC_WHU** | Li et al. 2019, ISPRS JPRS 150:197–212 (12.9, core) | Cloud vs clear. Thin cloud = cloud only where visible and the ground is not clearly seen. **No shadows.** Experts at Wuhan University (Photoshop lasso + magic wand) | Google Earth RGB, **0.5–15 m**, 150 images, 5 land-cover types (mirror: 120 train / 30 test, as 256 × 256 patches) | Official: **academic purposes only**. Mirror card: CC-BY-NC-4.0 | Official size not stated. Mirror `hrc_whu.zip` **115.5 MB** | Official: https://github.com/dr-lizhiwei/HRC_WHU → Google Drive https://drive.google.com/file/d/1qqikjaX7tkfOONsF5EtR4vl6J7sToA6p/view (or Baidu). Mirror: https://huggingface.co/datasets/XavierJiezou/cloud-adapter-datasets (file `hrc_whu.zip`) | Public Drive link; HF mirror readable without login. Not tested |
| AIR-CD | He, Sun, Yan & Fu 2021, DABNet, IEEE TGRS, https://doi.org/10.1109/TGRS.2020.3045474 (9.4, core) | Cloud only, pixel level, by experts | Gaofen-2 PMS, 4 m, NIR + visible, 34 scenes of 7,300 × 6,908 px | Not found | Not found; a search snippet says only part is uploaded | https://github.com/AICyberTeam/AIR-CD | Not verified (read: search snippet + OpenSICDR only) |
| GF2MS-WHU / GF1MS-WHU | Zhu, Li & Shen 2024, IEEE TGRS 62 (9.4, core) | Binary cloud. 29 GF-2 and 33 GF-1 images well annotated; the rest unlabelled | GF-2 MS 4 m; GF-1 PMS 8 m | Repo states none. Mirror card: CC-BY-NC-4.0 | Mirror zips: **1.74 GB** (GF-2), **0.94 GB** (GF-1) | https://github.com/whu-ZSC/GF1-GF2MS-WHU (Baidu Disk); mirror as above | Baidu usually needs an account (not verified); HF mirror open |
| T-PS / T-S2 | Shendryk et al. 2019 (venue not verified) | Block level (cloud, shadow, land-cover scene labels), per OpenSICDR | PlanetScope 3 m RGB + NIR (4,943 subscenes) and Sentinel-2 (4,993), 512 × 512 | Not read | Not read | https://data.mendeley.com/datasets/6gdybpjnwh/1 | Not read |
| **CloudSEN12** (CloudSEN12-high) | Aybar et al. 2022, *Scientific Data* 9:782 (JIF not in file; confirm in JCR) | **Clear, thick cloud, thin cloud, cloud shadow.** 14 domain experts with active learning and a four-step quality check; labellers recalibrated if overall accuracy fell below 90%. 10,000 high-quality patches, 10,000 scribble, the rest unlabelled | Sentinel-2 L1C/L2A (10 m) + Sentinel-1; about 49,400 patches of 509 × 509 px (the paper also says 49,250) | Article CC-BY 4.0. Data: HF `csaybar/CloudSEN12-high` card **CC-BY-NC-4.0**; Science Data Bank licence not read | Up to **1 TB**. CloudSEN12-high mirror zips **3.36 GB** (L1C) / **3.57 GB** (L2A) | https://cloudsen12.github.io/ ; Science Data Bank https://doi.org/10.57760/sciencedb.06669 ; https://huggingface.co/datasets/csaybar/CloudSEN12-high | HF not gated |
| KappaSet (KappaZeta) | Domnich et al. 2021, KappaMask, *Remote Sensing* 13:4100 (4.3, narrow; KappaZeta Ltd, company) | Clear, cloud shadow, semi-transparent (thin) cloud, cloud, invalid (abstract); labelling method not read | Sentinel-2, 4,403 blocks of 512 × 512 from 155 images, Northern Europe | Not read (Zenodo blocked scripted reads) | Not read | https://zenodo.org/record/5095024 | Zenodo usually open; not tested |
| L8 Biome | Foga et al. 2017, RSE 194:379–390 (12.3, core) | Manual masks. Thick, thin and shadow per CloudSEN12 Table 1; shadow in 32 of 96 scenes (OpenSICDR) | Landsat 8 OLI/TIRS, 30 m, 96 scenes | USGS page states no licence; data citation https://doi.org/10.5066/F7251GDH | Not stated. Preprocessed mirror **2.77 GB** | https://www.usgs.gov/landsat-missions/landsat-8-cloud-cover-assessment-validation-data | Not stated |
| SPARCS | Hughes & Hayes 2014, *Remote Sensing* 6:4907 (4.3, narrow) | Cloud and cloud shadow (no thin class per CloudSEN12 Table 1); labelling method not read | Landsat 8, 30 m, 80 subsets of 1,000 × 1,000 | Not read | Not read | USGS SPARCS page, linked from https://github.com/dr-lizhiwei/OpenSICDR | Not read |
| 38-Cloud / 95-Cloud | Mohajerani & Saeedi 2019, IGARSS (data attribution); 95-Cloud in Cloud-Net+ (arXiv 2001.08768) | Binary cloud, manual. **Thin cloud (haze) counts as cloud** | Landsat 8 RGB + NIR, 30 m. 38 scenes → 8,400 train + 9,201 test patches (384 × 384). 95-Cloud adds 57 training scenes (34,701 patches); same test set | Repo Apache-2.0 (38-Cloud); none stated (95-Cloud) | Not stated | https://github.com/SorourMo/38-Cloud-A-Cloud-Segmentation-Dataset (Kaggle, or a second server via a goo.gl link, unverified) | **Kaggle needs an account** |
| **WorldFloods v2** | Portalés-Julià et al. 2023, Sci. Rep. 13:20316 (4.9, core) | Separate clear/cloud and land/water masks. Flood maps from Copernicus EMS and others; manually labelled evaluation set of 11 events | Sentinel-2 (+ Landsat), 509 image–mask pairs | **CC-BY-NC-4.0** (dataset card) | About **76 GB**; **test split 3.16 GB** (90 files) | https://huggingface.co/datasets/isp-uv-es/WorldFloodsv2 ; flood maps https://zenodo.org/record/8153514 | HF not gated |
| WorldFloods v1 | Mateo-Garcia et al. 2021, Sci. Rep. 11:7249 (4.9, core) | Land, water, cloud (+ invalid). Cloud from s2cloudless (automatic) | Sentinel-2, 13 bands, 10 m; 256 × 256 tiles | v2 card says the WorldFloods database is CC-BY-NC | About **266 GB** | https://tinyurl.com/worldfloods (from the paper; not opened) | Not checked |
| Sen1Floods11 | Bonafilia et al. 2020, CVPR Workshops (company-led, Cloud to Street) | Hand labels: −1 no data / not valid, 0 not water, 1 water (446 chips). Whether cloud is coded −1 is unconfirmed | Sentinel-1 VV/VH + Sentinel-2 L1C (13 bands); 4,831 chips of 512 × 512 | Not read | About **14 GB** | `gs://sen1floods11` (Google Cloud Storage); https://github.com/cloudtostreet/Sen1Floods11 | Public bucket; no account mentioned (needs `gsutil`) |

**Nothing at 1 m or finer except HRC_WHU** (and HRC_WHU only partly, since it spans 0.5–15 m). The OpenSICDR catalogue, run by HRC_WHU's author and last updated June 2024, lists no other cloud set at 1 m or finer.

**For haze (not cloud labels):** RS-Haze (DehazeFormer) gives synthetic hazy/clear RGB pairs on Google Drive (README); size and licence not read.

---
