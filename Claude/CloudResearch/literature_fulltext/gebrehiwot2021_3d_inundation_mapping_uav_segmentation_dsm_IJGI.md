# Coder handoff: Gebrehiwot & Hashemi-Beni (2021), Three-dimensional inundation mapping using UAV image segmentation and digital surface model

- **Citation:** Gebrehiwot, A. A., & Hashemi-Beni, L. (2021). Three-dimensional inundation mapping using UAV image segmentation and digital surface model. *ISPRS International Journal of Geo-Information* 10(3), 144. https://doi.org/10.3390/ijgi10030144 (CC BY 4.0)
- **PDF:** `/Users/jusrogers/Masters/papers/gebrehiwot2021_3d_inundation_mapping_uav_segmentation_dsm_IJGI-summary.pdf` (page 1 = AI summary; paper pages follow)
- **Source:** MDPI publisher PDF downloaded through Justin's session (staging copy in `papers/_incoming_gmu/`, deleted after the merge checked out). Supersedes claim_checks_C, where the MDPI PDF was blocked.
- **Validation:** real PDF (`file`: PDF document; 1.3 MB). Read tool and pdfinfo: 14 pages = article pages "1 of 14" to "14 of 14". Page-1 title, both authors, ISPRS Int. J. Geo-Inf. 2021, 10, 144 and DOI match. §5 Conclusions (pp. 11–12) and references 1–42 (pp. 12–14) present. PASS. (`file` metadata says 10 pages; ignored.)
- **Read:** pp. 1–14 in full (page images), all figures and tables.
- **Prepared by:** Claude (AI), 2026-10-30. Page numbers are the article's. NC A&T State University; NSF-funded. JIF of IJGI not checked here ("confirm in JCR" stands).

## 1. Method, step by step (§3, pp. 4–7, Fig. 2)
Three stages; two variants differ only in stage 2.

1. **Stage 1, 2-D flood extent** (p. 5): FCN-8s (VGG16 backbone, from the authors' 2019 *Sensors* paper), fine-tuned on **150 hand-annotated UAV images** (4000 × 4000 px), SGD, 6 epochs, lr 0.001, batch ≤ 2. Classes: water, others (buildings etc.), vegetation. Georeferenced with 8 GCPs; raster → polygons.
2. **Stage 2, water surface:**
   - **Method 1, SfM + CNN** (pp. 5–6, 8–9): Pix4D SfM on 1,800 UAV images (80% overlap, 4 GCPs); flood polygons classify the SfM point cloud into water/non-water; noise removal; "hydro-flattened" (water bodies flat bank to bank, one elevation per polygon); natural-neighbour interpolation → water DEM at **10 cm**.
   - **Method 2, DEM + CNN** (p. 6, 9): intersect each flood polygon with the pre-flood LiDAR DEM; water elevation per polygon = **mean DEM elevation of polygon vertices on true water/dry interfaces**, excluding vertices on water–vegetation and water–building edges (ambiguous); constant water surface per polygon; raster at 10 cm.
3. **Stage 3, depth** (eq. 1, p. 7): `ID = H − h`, H = water-surface elevation, h = pre-flood DEM.
4. **Evaluation** (p. 7): RMSE of depth against USGS gauge "elevation"/water-level data. The number of gauges, their locations and the comparison time are **not reported**.

## 2. Inputs, outputs, data needs
- UAV RGB at **2.6 cm** (Trimble UX5 fixed-wing), North Carolina Emergency Management, Hurricane Matthew 2016 (p. 4).
- Pre-flood LiDAR 2014, **2 pts/m², 9.25 cm RMSE**, interpolated to a 10 cm DEM (pp. 4, 9).
- USGS gauge water levels; MATLAB, Pix4Dmapper, ArcGIS; Xeon + Quadro M4000 (p. 7).
- Study area: Princeville, NC, on the Tar River.
- **Inconsistency in the paper:** p. 4 and the abstract say Princeville imagery was from Hurricane Matthew; p. 5 says the model was trained on Matthew imagery from **Lumberton** and tested on "the Hurricane **Florence** image collected over the city of Princeville". Fig. 4 shows Lumberton (Matthew, Oct 2016) training samples.
- Data availability: "Data sharing not applicable" (p. 12).

## 3. Quantitative results to compare against
- FCN-8s confusion matrix (Table 1, p. 8): water 98.71%, others 95.52%, vegetation 98.43%; OA ≈ 97%, kappa 0.934 (p. 7). It is not stated whether this is on the Princeville test image or on held-out Lumberton images.
- Max depth: method 1 = 1.86 m, method 2 = 2.2 m, both in the river channel (p. 10). (Fig. 7 colour bars read 2.2 and 1.9, swapped relative to the text.)
- Method 2 − method 1 per cell: |diff| 0.001–0.4 m; mean 0.2 m, SD 0.1 m (p. 10, Fig. 8).
- **RMSE vs gauge: method 1 (SfM) 0.34 m, method 2 (DEM) 0.26 m** (abstract; p. 10; p. 11–12). No n, no significance test, no spatial validation away from the gauge(s).

## 4. Stated limitations
- Constant water level per polygon "may not completely accurate for extreme events due to complex flow paths" (p. 6).
- Water–vegetation and water–building edges do not mark the true shoreline (p. 6).
- SfM voids over homogeneous water (insufficient tie points); voids were interpolated (p. 9).
- Depth quality depends on DEM quality and extent-map quality (p. 11). Future: more in-situ validation, resolution and DEM effects (p. 12).

## 5. How to apply to our pipeline
- **Method 2 is the depth recipe closest to our possible road-depth label** (evidence 19 rec. 8): a flood polygon from imagery + a pre-flood LiDAR DEM (3DEP 1 m for Ida) → one water elevation per polygon from shoreline vertices → depth = water − DEM. It needs no flood-time LiDAR or SfM, unlike Chen 2017 and method 1.
  - numpy/rasterio recipe: label connected flood components (`scipy.ndimage.label`); boundary pixels = component minus its erosion; **drop boundary pixels adjacent to building or tree masks** (the paper's key rule); water level = mean (or median, more robust) DEM over the remaining boundary pixels; depth = clip(level − DEM, 0, None) inside the component; flag components with < N clean boundary pixels.
  - Their use of the **mean** of shoreline vertices is sensitive to a few high vertices; report median as well. Compare with FwDET's nearest-boundary-cell approach (Cohen 2018/2019 handoffs).
- **Evidence weight for the 0.26 m figure:** one event, gauge validation with unstated n, no uncertainty. Cite it as "RMSE 0.26 m against USGS gauge water levels (number of gauges not reported)". It sits inside the 0.18–0.5 m range of evidence 19 l. 404 but is too thin to set a margin on its own.
- **Not usable for our cloud problem:** UAV at 2.6 cm under the cloud deck; no cloud handling.

## 6. Key quotes
- "The RMSEs for water depth using the SfM method and integrated method based on deep learning and DEM were 0.34m and 0.26m, respectively." (abstract, p. 1)
- "This approach assumes that the water surface of the flooded areas is flat and has constant water elevation inside each detected flood/water polygon." (p. 6)
- "the line segments resulting from the intersection of water and vegetation polygons or water and building polygons do not necessarily represent the interfaces between dry and water areas" (p. 6).
- "The Hurricane Matthew UAV images acquired in the city of Lumberton in 2016 were used to train the FCN-8s model, whereas the Hurricane Florence image collected over the city of Princeville was used to test the model." (p. 5)
