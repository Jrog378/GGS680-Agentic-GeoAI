# Coder handoff: Lin, Xu, Wang, Wang, Sun & Fu (2019), RICE cloud-removal dataset (data note)

- **Citation:** Lin, D., Xu, G., Wang, X., Wang, Y., Sun, X., & Fu, K. (2019). A remote sensing image dataset for cloud removal. arXiv:1901.00600v1 [cs.CV] (3 Jan 2019). Institute of Electronics, CAS. Preprint, not peer reviewed; OpenAlex lists no journal version of this title. Data: https://github.com/BUPTLdy/RICE_DATASET
- **PDF:** `/Users/jusrogers/Masters/papers/lin2019_rice_cloud_removal_dataset_arXiv-summary.pdf` (page 1 = AI summary)
- **Source:** https://arxiv.org/pdf/1901.00600 (only version).
- **Validation:** PDF 6.5 MB, 4 pages (Read tool, pages 2–4 read as images; pdfinfo agrees); title/authors match the arXiv record; Conclusion (§4) and one reference present. No DOI other than the arXiv DOI 10.48550/arXiv.1901.00600. PASS (short data note).
- **Read:** pp. 1–4 in full, including Figures 1–2.
- **Prepared by:** Claude (AI), 2026-10-29.

## 1. What the dataset is (§2, p. 3–4)
- **RICE-I:** 500 pairs, 512 × 512, from **Google Earth by toggling the display of the cloud layer** ("the corresponding cloud and cloudless images are obtained by setting whether to display the cloud layer"), cut without overlap. So the cloudy image is a rendered overlay over the same base imagery, not an independent acquisition. Fig. 1 shows thin, hazy veils (desert, mountains, water). Resolution, dates and locations not stated.
- **RICE-II:** **450 sets** of (cloudy, mask, clear), 512 × 512, from Landsat 8 **LandsatLook** products: "Natural Color" = OLI **bands 6, 5, 4 (SWIR1, NIR, red)** — the paper itself calls it false colour; mask from the LandsatLook Quality image (fill black, cloud white, **cloud shadow blue, cirrus yellow**); clear image of the same place chosen manually, **< 15 days apart**.
- No train/test split, no labelling protocol beyond the above, no licence statement in the paper.

## 2. Baseline (§3, p. 4)
- pix2pix; for RICE-II the mask is concatenated to the input. Table 2: **RICE-I PSNR 31.03 / SSIM 0.91; RICE-II 30.04 / 0.80**. Split and training details not given.

## 3. Discrepancies with how others describe RICE
- DE (Sui et al. 2024, Table I) lists **RICE2 = 736 images** and both parts as 30 m, 3 bands; this paper says **450 sets** and gives no resolution for RICE-I. DE's 35 dB scores on RICE are on whatever split DE drew (8:2 random).

## 4. Limitations (our reading; the paper states none)
- RICE-I "clouds" are a display layer: perfectly co-registered, same instant, no illumination change — easier than real clouds and not physically a cloud over the scene.
- RICE-II is false colour (SWIR/NIR/red) at Landsat resolution.
- 4-page note; no split, no protocol, no variance.

## 5. How to apply to our pipeline
- **Do not use RICE scores as evidence for 0.5 m RGB cloud handling.** High PSNR on RICE (31–35 dB) reflects an easy, synthetic-overlay pair (RICE-I) or 30 m false colour (RICE-II).
- **RICE-I as a haze-recovery sanity set (optional, display-only):** its veils resemble thin haze and come with an exact clear counterpart. It could be a quick extra check for `sn8_clouds.dehaze` (single-date dark channel) — but it is Google Earth imagery with unknown provenance/licence; treat as an informal check, not evidence, and do not train on it.
- **RICE-II structure** (cloudy + cloud/shadow/cirrus mask + clear ≤ 15 days) is the right template if we ever build real paired data; shadow is a separate mask class there, unlike HRC_WHU.
- **Feasibility:** small (950 items); downloads are datasets, out of scope for this brief.

## 6. Key quotes
- "the corresponding cloud and cloudless images are obtained by setting whether to display the cloud layer" (p. 3)
- "The LandsatLook Natural Color image is a composite of Three bands (Landsat 8 OLI, Bands 6,5,4) to show a 'natural' looking (false color) image." (p. 4)
- "we manually selected a cloudless image at the same location with a cloud image time less than 15 days apart" (p. 4)
