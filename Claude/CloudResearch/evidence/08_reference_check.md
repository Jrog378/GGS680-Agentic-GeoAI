# 08: Reference check for the deck, and three SpaceNet 8 facts (2026-10-25)

Bibliographic check, not our own measurements.

**Method:**
- Each DOI was checked against its Crossref record, `https://api.crossref.org/works/<doi>`. Crossref holds the
  metadata the publisher registered.
- Extra sources, used only where needed:
  - the TMLR site, for DINOv2, which has no DOI;
  - the CVF Open Access page and PDF, for SpaceNet 8;
  - OpenAlex, for the Haralick abstract;
  - the arXiv accepted manuscript, to confirm Li et al. named HRC_WHU.
- No logins were used and no paywalled PDFs were downloaded.
- Three sites showed bot checks, which were not solved: OpenReview, DBLP and IEEE Xplore.
- **Author rule:** a work with more than three authors is written as the first three plus "et al.".
- **Blank fields:** a field is left blank only when no source gives it.

## 1. References

| # | Reference (compact) | Status | Notes vs. the local/slide entry |
|---|---|---|---|
| 1 | He, K., Sun, J., & Tang, X. (2011). Single image haze removal using dark channel prior. *IEEE Transactions on Pattern Analysis and Machine Intelligence* 33(12), 2341–2353. doi:10.1109/TPAMI.2010.168 | **VERIFIED**: [Crossref](https://api.crossref.org/works/10.1109/TPAMI.2010.168) | Matches. |
| 2 | Li, Z., Shen, H., Cheng, Q., et al. (2019). Deep learning based cloud detection for medium and high resolution remote sensing images of different sensors. *ISPRS Journal of Photogrammetry and Remote Sensing* 150, 197–212. doi:10.1016/j.isprsjprs.2019.02.017 | **VERIFIED**: [Crossref](https://api.crossref.org/works/10.1016/j.isprsjprs.2019.02.017); [arXiv:1810.05801](https://arxiv.org/abs/1810.05801) | **Authors:** 6, the other three being Liu, Y., You, S. and He, Z. **Issue:** none; the journal assigns volumes only. **Title:** it opens "Deep learning based" and says "remote sensing images". **HRC_WHU:** the accepted manuscript (arXiv, p. 15 of the PDF) says "HRC_WHU was created in this study". |
| 3 | Oquab, M., Darcet, T., Moutakanni, T., et al. (2024). DINOv2: Learning robust visual features without supervision. *Transactions on Machine Learning Research* (ISSN 2835-8856). https://openreview.net/forum?id=a68SUt6zFt | **VERIFIED**: [TMLR paper list](https://jmlr.org/tmlr/papers/), [TMLR BibTeX](https://jmlr.org/tmlr/papers/bib/a68SUt6zFt.bib), [arXiv:2304.07193](https://arxiv.org/abs/2304.07193) | **Authors:** 26. **Date:** published January 2024, with a Featured Certification. **Missing fields:** the TMLR record gives no volume, issue, pages or DOI, so these are left blank. The arXiv record has no DOI either. |
| 4 | Haralick, R. M. (1979). Statistical and structural approaches to texture. *Proceedings of the IEEE* 67(5), 786–804. doi:10.1109/PROC.1979.11328 | **VERIFIED**: [Crossref](https://api.crossref.org/works/10.1109/PROC.1979.11328); abstract from [OpenAlex](https://api.openalex.org/works/doi:10.1109/PROC.1979.11328) | Matches. The summary is below the table. |
| 5 | Roberts, D. R., Bahn, V., Ciuti, S., et al. (2017). Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography* 40(8), 913–929. doi:10.1111/ecog.02881 | **VERIFIED**: [Crossref](https://api.crossref.org/works/10.1111/ecog.02881) | **Authors:** 14. **Title:** it has a serial comma, "hierarchical, or phylogenetic". **Date:** online 3 Mar 2017; the issue is Aug 2017. |
| 6 | Canty, M. J., & Nielsen, A. A. (2008). Automatic radiometric normalization of multitemporal satellite imagery with the iteratively re-weighted MAD transformation. *Remote Sensing of Environment* 112(3), 1025–1036. doi:10.1016/j.rse.2007.07.013 | **VERIFIED**: [Crossref](https://api.crossref.org/works/10.1016/j.rse.2007.07.013) | The local 112(3):1025–1036 and DOI are correct. The full title includes "of multitemporal satellite imagery". |
| 7 | Breiman, L. (2001). Random forests. *Machine Learning* 45(1), 5–32. doi:10.1023/A:1010933404324 | **VERIFIED**: [Crossref](https://api.crossref.org/works/10.1023/A:1010933404324) | Matches. |
| 8 | McNemar, Q. (1947). Note on the sampling error of the difference between correlated proportions or percentages. *Psychometrika* 12(2), 153–157. doi:10.1007/BF02295996 | **VERIFIED**: [Crossref](https://api.crossref.org/works/10.1007/BF02295996) | The full title ends "or percentages". |
| 9 | Hänsch, R., Arndt, J., Lunga, D., et al. (2022). SpaceNet 8 – The detection of flooded roads and buildings. In *2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops (CVPRW)*, 1471–1479. doi:10.1109/CVPRW56347.2022.00153 | **VERIFIED**: [Crossref](https://api.crossref.org/works/10.1109/CVPRW56347.2022.00153); [CVF page](https://openaccess.thecvf.com/content/CVPR2022W/EarthVision/html/Hansch_SpaceNet_8_-_The_Detection_of_Flooded_Roads_and_Buildings_CVPRW_2022_paper.html) | **Authors:** 8. **Pages:** the local 1471–1479 matches the IEEE/Crossref record. The CVF Open Access copy is numbered **1472–1480**, one page later, and the page numbers in section 2 below are CVF's. **Spelling:** Crossref writes "Hansch"; the CVF copy writes "Hänsch". |
| 10 | Portalés-Julià, E., Mateo-García, G., Purcell, C., et al. (2023). Global flood extent segmentation in optical satellite images. *Scientific Reports* 13(1), 20316. doi:10.1038/s41598-023-47595-7 | **VERIFIED**: [Crossref](https://api.crossref.org/works/10.1038/s41598-023-47595-7) | **Authors:** 4, the fourth being Gómez-Chova, L. **Article number:** 20316, with issue 1. **Date:** published 20 Nov 2023. |
| 11 | Qu, Y., Li, J., & Huang, X. (2026). AnyTime-CD: Self-supervised change detection in arbitrary-length dense time series of high-resolution remote sensing images. *Remote Sensing of Environment* 334, 115239. doi:10.1016/j.rse.2026.115239 | **VERIFIED**: [Crossref](https://api.crossref.org/works/10.1016/j.rse.2026.115239) | **Title:** the subtitle is "Self-supervised change detection in…". **Issue:** none. **Date:** issued March 2026. **Name:** Crossref spells the second author "JiaYi Li". |
| 12 | Shen, H., Li, X., Cheng, Q., et al. (2015). Missing information reconstruction of remote sensing data: A technical review. *IEEE Geoscience and Remote Sensing Magazine* 3(3), 61–85. doi:10.1109/MGRS.2015.2441912 | **VERIFIED**: [Crossref](https://api.crossref.org/works/10.1109/MGRS.2015.2441912) | **Authors:** 7. |
| 13 | Bruzzone, L., & Bovolo, F. (2013). A novel framework for the design of change-detection systems for very-high-resolution remote sensing images. *Proceedings of the IEEE* 101(3), 609–630. doi:10.1109/JPROC.2012.2197169 | **VERIFIED**: [Crossref](https://api.crossref.org/works/10.1109/JPROC.2012.2197169) | The full title ends "remote sensing images". |

**Haralick (1979), summary from the abstract:** The paper surveys the image-processing literature on texture. It
reviews:
- statistical methods: the autocorrelation function, optical and digital transforms, textural edgeness, structural
  elements, grey-tone co-occurrence, run lengths and autoregressive models;
- structural approaches built on primitives more complex than grey tone;
- hybrid structural-statistical methods, which apply the statistical techniques to those primitives.

## 2. SpaceNet 8 facts

The source is the free CVF Open Access PDF of Hänsch et al. (2022), 9 pages, printed pp. 1472–1480. The page numbers
below are its printed numbers. The IEEE Xplore copy is numbered one page lower, which gives the "1471–1479" in the
DOI record. Its page numbers below are inferred from that offset, not checked against the IEEE PDF.

### 2a. Acquisition dates of the Louisiana imagery, and the sensor or provider
- **Dates:** the paper gives no pre-event or post-event acquisition date. It gives only the event timing:
  - "Louisiana after Hurricane Ida end of August 2021" (p. 1474, §2 Data);
  - Figure 3 (p. 1474) says the imagery was acquired "before and after a flood in 2021".
- **The name "Louisiana-East":** the paper never uses it. It has one Louisiana area of interest ("L", 741.1 km² in
  Table 1, p. 1475). The East/West split comes only from the data release: the `Louisiana-East_Training_Public` and
  `Louisiana-West_Test_Public` tarballs listed on spacenet.ai.
- **Provider:** the Maxar Open Data Program. The paper uses "pansharpened RGB (0.3-0.8m resolution) data routinely
  published through the Open Data Program" (p. 1474).
- **Sensor:** not named beyond "Maxar's Earth observation satellites" (p. 1473). Pre-event and post-event tiles have
  different resolutions (p. 1475).
- **Twelve images:** the paper uses twelve images in total, pre-event and post-event across the AOIs, for training and
  scoring (p. 1474).
- **Supplement, from our local file:** the release file `Louisiana-East_Training_Public_label_image_mapping.csv`
  (599 tiles) lists Maxar catalog IDs.
  - **Pre-event:** `10400100684A4B00` (333 tiles), `10300100AF395C00` (139) and `105001001A0FFC00` (127).
  - **Post-event:** `10300100C46F5900` (all 599).
  - **Not verified:** the dates and satellites for these IDs. Maxar's Hurricane Ida open-data page failed with an
    expired TLS certificate, and Ida 2021 is not in Maxar's open-data STAC catalog.
- **Germany dates disagree:** the paper says Germany was flooded in "early July 2021". The spacenet.ai page says "June
  2021" for Germany and "August 2021" for Louisiana.

### 2b. Dataset licence
- **Paper (p. 1473, §2 Data):** "The imagery is released under a Creative Commons 4.0 Non-Commercial License". This
  sentence is about the Maxar Open Data imagery.
- **spacenet.ai, SN8 page** ([spacenet.ai/sn8-challenge](https://spacenet.ai/sn8-challenge/), shown on the page, not in
  an HTML comment): "licensed under a Creative Commons Attribution-ShareAlike 4.0 International License". This
  sentence covers "The SpaceNet Dataset by SpaceNet Partners".
- **AWS Open Data registry** ([registry.opendata.aws/spacenet](https://registry.opendata.aws/spacenet/)): "Various (See
  here for more details)". The "here" link goes to spacenet.ai/datasets/.
- **The two sources disagree:** the paper says Non-Commercial for the imagery, while the site says BY-SA for the
  dataset.
  - The paper and the site do not say which licence covers the imagery and which the labels.
  - The Maxar Open Data page itself was unreachable. A search snippet of that page says CC BY-NC 4.0, but that was not
    checked directly.
  - For the fully open route, assume the imagery is non-commercial.

### 2c. The "only attribute what was visible" instruction
- **Answer:** yes.
- **Where:** p. 1474 of the CVF copy (PDF page 3), §2 Data, right column. In IEEE Xplore pagination that is probably
  p. 1473, which is inferred, not checked.
- **Context:** the instruction applies when cloud cover obscured features in the post-event image. Analysts "were
  instructed to only attribute what was visible", without assuming anything about features they could not see.
- **Conclusion (p. 1478):** the paper repeats that the imagery includes "realistic challenges such as cloud cover".

## Sources checked
- **Crossref:** the 12 DOI records linked in the table.
- **DINOv2:** the TMLR paper list and BibTeX, and the arXiv API record for 2304.07193.
- **Haralick:** OpenAlex for the abstract. Semantic Scholar and IEEE Xplore gave no usable abstract.
- **Li et al.:** the arXiv API record and the accepted manuscript for 1810.05801.
- **SpaceNet 8:** the CVF Open Access HTML and PDF, spacenet.ai/sn8-challenge and registry.opendata.aws/spacenet.
- **Blocked or not used:** OpenReview and DBLP showed bot challenges, which were not solved. The IEEE Xplore page needs
  JavaScript. maxar.com/open-data/hurricane-ida failed with an expired certificate.

## Haralick 1979, full text (2026-10-26 00:05; Justin's GMU download, saved as `~/Masters/papers/haralick1979_statistical_structural_texture_ProcIEEE.pdf`)
- Read pp. 786–788 and 791–792 of the full text, a genuine IEEE Xplore copy licensed to George Mason University.
- p. 787: "spatial gray tone cooccurrence probabilities" is one of the eight statistical approaches the survey reviews.
- p. 787: probability (equal-frequency) quantizing makes the co-occurrence approach invariant under monotonic grey-tone
  transformations. This matches `sn8_glcm.GLCM_LEVELS`: 32 equal-probability grey levels per date.
- pp. 791–792: co-occurrence matrices P(i, j, d, θ) at 0°, 45°, 90° and 135°.
- Fig. 7 lists the common features: uniformity/energy, entropy, maximum probability, contrast, inverse difference
  moment and correlation.
- Our `GLCM_PROPS` are contrast, homogeneity, ASM (= uniformity/energy), entropy and correlation. Four match Fig. 7
  directly. Homogeneity is a variant of the inverse difference moment.
- Verdict: the slide's attribution ("Texture features · Proc. IEEE") is supported by the full text. Slide 12's
  "(abstract checked)" was removed on 25 Oct and is now justified.
