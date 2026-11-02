# 10: Is our ring and cloud removal backed by the experts? Literature check (2026-10-25)

**Request (Justin, 2026-10-25):** "Look for research backed methods to ensure that everything we are doing to remove the
ring and the cloud are backed by industry experts opinions".
**Checked against:** `ProjectBranch/ClaudeFunctions/sn8_refhaze.py` (`cloud_gate`, `tone_curve`,
`dark_reference_dehaze`), `sn8_clouds.py` (`dark_channel`, `guided_filter`, constants) and the ring arms in
`sn8_cloudedge.py` (evidence 09's agent). All were read only; no code or slide was changed.
**Compiled by:** Claude (AI research assistant), working alone. This is a literature note, not our own measurements.

**Method:**
- **Disk first.** Read in full: Zhu & Woodcock 2012 (Fmask), Canty & Nielsen 2008 (IR-MAD) and Canny 1986, from
  `~/Masters/GGS680/references/`; Claverie et al. 2018 (HLS), from `~/Claude/Personal/research/.../pdfs/`. Also
  re-used evidence 02, 05, 07 and 08, and `ProjectBranch/Literature/notes/clouds.md`. `~/Masters/papers/` has nothing
  on haze or cloud.
- **Open web, no logins.** Full texts read from authors' or institutional open copies: He, Sun & Tang 2011 and 2013
  (Kaiming He's MIT page), Zhu, Wang & Woodcock 2015 (GERS lab, UConn) and Shen et al. 2015 (WHU SENDIMAGE author
  manuscript). The fetch tool cached these PDFs in the session's tool-results folder, outside the project; nothing was
  saved into the project or `papers/`.
- **Abstracts** came from OpenAlex, from the publisher's record via Crossref, or from NASA/NTRS pages.
- **References.** Every DOI below was checked against its Crossref record (`api.crossref.org/works/<doi>`) on
  2026-10-25. Requests carried a generic user agent only, with no email or other identifier.
- **Blocked, not bypassed:** MDPI, the CVF page for Cloud Score+, roderic.uv.es (CMIX PDF), the CESBIO/Theia MAJA pages
  (connection reset), the PCI Catalyst help, AGU's and ACM's impact-factor pages (403), and NRCan's HOT preprint (404).
  Semantic Scholar rate-limited after two calls.

**Labels:**
- **Read depth:** *full text*, *abstract*, *metadata* (title and venue only), or *secondary* (another paper's account
  of it).
- **Venue:** JIF values are from `Project/docs/literature/journal_impact_factors.md` unless marked. Values found in this
  session are marked **(new)** with their source. Major conferences (CVPR/ICCV/ECCV) and company-led papers qualify
  without a JIF.
- **Agency documents** (USGS, NASA, CNES) and the Fmask software README are *operational practice*. They are not
  peer-reviewed and are reported in their own rows.
- **Voice:** "States" is what the source did or wrote; "My read" is my inference.

---

## In short

1. **The ring is the halo the dark channel's authors describe, and we have switched off their fix.**
   - He, Sun & Tang (2011, TPAMI, full text) say the raw transmission map's "main problems are some halos and block
     artifacts. This is because the transmission is not always constant in a patch." They fix it with soft matting,
     and in 2013 with the guided filter.
   - The authors' own guided-filter recipe has a step we do not use. They "first apply a max filter to counteract the
     morphological effects of the min filter", then filter "under the guidance of the hazy image" (He, Sun & Tang 2013,
     §5, full text).
   - Our `dark_channel` erodes with a 41 px minimum filter, then box-blurs over 41 px. No max filter follows, and
     `DARKREF_GUIDED` is off.
   - My read: the haze edge in t sits inside the true cloud edge. That leaves an under-corrected band at the edge, which
     is the ring.
2. **Operational cloud masks all dilate the cloud, because its edges are thin cloud.**
   - Zhu, Wang & Woodcock (2015, RSE, full text): "The pixels surrounding clouds and cloud shadows are masked out in
     the Fmask algorithm because many of these pixels may still be influenced by the thin edges of clouds and their
     shadows."
   - The same practice appears in LaSRC (150 m adjacency windows; Claverie et al. 2018), USGS Collection 2 (a "Dilated
     Cloud" QA bit), the Fmask software (3 px by default) and Google Earth Engine's s2cloudless tutorial (50–100 m).
   - Two NASA GRL studies find haze and brightening extending well past detected clouds: tens of km (Koren et al. 2007)
     and about 15 km (Várnai & Marshak 2009).
   - So a soft or dilated gate (arm a) has the strongest practical backing. But every operational system *masks* the
     buffer. Correcting inside the buffer is our own extension.
3. **The guided filter is the right family, but guiding it with the BEFORE image is not what the experts did.**
   - The guided filter "can transfer the structures of the guidance image to the filtering output" (He et al. 2013).
     Joint-filtering papers warn that where guide and target edges differ, "simply passing all patterns to the target
     could introduce significant errors" (Shen et al. 2015, ICCV). Ham, Cho & Ponce (2018, TPAMI) make the same point.
   - My read: in change detection, a before-image guide would print pre-flood structure into the corrected after image.
     Arm (c) as specified is only partly supported. Evidence 09's "texture copied" guard tests exactly this risk.
4. **Leaving opaque cloud as "cannot assess" is supported.**
   - Shen et al. (2015, GRSM, full text) define missing data as information "completely obscured or not observed".
     They state that temporal methods "are sensitive to land-cover changes, especially abrupt changes".
   - He et al. (2011) bound t below (t0 = 0.1) because the restored image "is prone to noise" where t is small.
   - SpaceNet 8 annotators "were instructed to only attribute what was visible" (evidence 08).
   - Our T_MIN = 0.2 and the choice to abstain rather than restore are our own, stricter rule.
5. **Matching the two dates' tones over clear pixels is established, but on invariant pixels.**
   - The radiometric-normalisation experts (Schott 1988; Du et al. 2002; Canty & Nielsen 2008) normalise on
     time-invariant pixels.
   - USGS used histogram matching, and later local linear histogram matching, to fill Landsat SLC-off gaps. Shen et al.
     (2015) say this works "if the input scenes are of high quality" but struggles in heterogeneous landscapes.
   - Our tone curve uses all clear pixels, including flood-changed ground. That part has partial support at best.

---

## 1. Our steps against the literature

Verdicts: **supported**, **partly** (the idea is supported but our form or setting is not), **not supported** (the
literature argues against it), **our own rule** (no source either way).

| Our step | Source (venue; JIF or company; read depth) | What the source says, in one line | Verdict |
|---|---|---|---|
| **1. Cloud/haze mask = dark-channel rise between dates** | He, Sun & Tang 2011 (IEEE TPAMI; 18.6, 2024 value; full text) | "The dark channel of a hazy image approximates the haze denseness" (§4.3); it is used to find the most haze-opaque region | **Supported** (dark channel as a haze measure) |
| 1, two-date form | Hagolle et al. 2010 (RSE; 12.3; abstract via a search summary, no full text) | Multi-temporal cloud detection: a per-pixel jump in blue reflectance against the previous image, plus a neighbourhood linear-correlation test; implemented in CNES's MAJA | **Partly**: a precedent for "rise against a clear reference", but in blue reflectance, not the dark channel |
| 1, two-date form | Lin et al. 2015 (ISPRS JPRS; 12.9; abstract via a search summary) | Multi-temporal cloud detection "mainly relies on the successful radiometric correction/normalization and reference image quality"; builds the reference from weighted invariant pixels | **Partly**: same family. It warns that the rise is only as good as the matching (step 2) |
| 1, the thin edge | Zhu, Wang & Woodcock 2015 (RSE; 12.3; full text) | "Optically thin clouds are difficult to detect as they may have spectral signatures similar to the Earth surface underneath" | Explains why a single cut misses the fringe (the ring) |
| 1, the thin edge | Skakun et al. 2022, CMIX (RSE; 12.3; CEOS team with CNES, ESA, DLR, NASA, USGS and companies; abstract) | Ten operational algorithms agreed on thick, opaque cloud, "in contrast to thin/semi-transparent clouds detection" | Same: the fringe is where every mask is least sure |
| 1, 41 px window | He et al. 2011 (as above) | They use 15 × 15 on 600 × 400 images; a larger patch makes the prior more valid, but "if the patch size is too large, halos near depth edges may become stronger" (§4.5) | **Our own rule**. The trade-off it sits on is He's |
| 1, the box blur after the min filter (`dark_channel`) | He et al. 2011; He et al. 2013 (TPAMI; 18.6; MSRA, company; full text) | He's dark channel is the minimum filter alone. To refine t, He first applies "a max filter to counteract the morphological effects of the min filter" | **Not supported**: our blur is an addition He does not make, and the max-filter step is missing (§3) |
| 1, blobs ≥ 2,500 m² | Zhu & Woodcock 2012, Fmask (RSE; 12.3; full text, p. 88) | "For cloud objects less than 3 pixels, Fmask excludes them from cloud mask … as most of them are misidentification of small bright cold noncloud pixels" | **Partly**: a minimum object size is standard. Our 2,500 m² (roofs, debris) is our own value. Three 30 m pixels is 2,700 m², but that is a noise rule at another scale |
| 1, blobs ≥ 2,500 m² | Guan, Khadka & Gerard, US 9,721,181 B2 (2017; The Climate Corporation; company patent, not peer-reviewed; description read) | Cloud seeds and candidates are cleaned by morphological opening with 20 m and 40 m radius discs; an urban detector removes bright built-up areas | Precedent only (patent): object-scale cleaning against bright roofs at our scale |
| **2. Tone matching of the dates = quantile matching on clear pixels** | Canty & Nielsen 2008 (RSE; 12.3; full text, on disk) | Relative normalisation assumes a linear relation over "regions of constant reflectance"; "the critical aspect is the determination of suitable time-invariant features"; cloud pixels were "correctly identified as change" | **Partly**: normalising from the image pair is the expert practice, but on invariant pixels, and linear |
| 2 | Nielsen 2007, IR-MAD (IEEE TIP; 13.7, 2024 value; abstract) | Iterations give "large weights … to observations that show little change", i.e. the fit is driven by no-change pixels | **Partly**: argues for dropping changed (flooded) pixels from the fit |
| 2 | Schott, Salvaggio & Volchok 1988 (RSE; 12.3; metadata; cited by Canty & Nielsen); Du, Teillet & Cihlar 2002 (RSE; 12.3; abstract, read for evidence 05) | Pseudo-invariant features; statistically chosen PIFs with quality control *for land-cover change detection* | **Partly**, as above |
| 2, histogram matching itself | Shen et al. 2015 (IEEE GRSM; 13.7; full text, author manuscript, §V-A) | USGS EROS filled SLC-off gaps with "a simple histogram matching method", then local linear histogram matching in a moving window. It "can perform well in most regions if the input scenes are of high quality" but "has difficulty with heterogeneous landscapes" | **Partly**: an agency precedent for histogram matching between dates, with stated limits |
| 2, nonlinear curve | – | No JIF > 4 source found on Maxar's 8-bit visual product tone curves | **Our own rule** (education briefing P3) |
| 2, clear pixels kept only 10 m from the gate | Zhu et al. 2015; Koren et al. 2007 (GRL; 5.0 **(new)**, 2025 value, aggregator journalmetrics.org only; NASA GSFC/Weizmann; abstract); Várnai & Marshak 2009 (GRL; same; NASA GSFC; abstract) | Pixels next to clouds are still influenced by thin edges; clouds are surrounded by a "twilight zone … extending tens of kilometers"; clear-sky brightening "extends to about 15 km away from clouds" | **Partly**. My read: some "clear" pixels in the tone fit are near-cloud haze; the 10 m margin has no published basis |
| **3. Haze model I = J t + A(1 − t)**, with the before image's dark channel in place of "dark channel ≈ 0" | He et al. 2011 (full text, eqs. 8–11 and 13) | t is taken as constant in a patch, so the dark channel of I is t times the dark channel of J plus (1 − t); the prior (J's dark channel = 0) is then used to remove the J term. Eq. 13 generalises to separate t1, t2 | **Supported**: our t = (A − dark(after)) / (A − tone(dark(before))) is eq. 8 with J's dark channel measured instead of assumed |
| 3, reference-based variant | Lin et al. 2015 (as above); Hagolle et al. 2010; Hagolle et al. 2015 (Remote Sensing 4.3, narrow; abstract; evidence 05) | Clear references from other dates, for cloud detection and for aerosol (haze) correction; the multi-temporal aerosol method assumes stable surface reflectance and degrades when the landscape changes very quickly | **Partly**: multi-temporal haze correction is established (CNES). No published single-band VHR dark-channel variant was found (gap, as in evidence 05) |
| 3, haze thickness at VHR | Makarau et al. 2014 (IEEE TGRS; 9.4; DLR; abstract) | Dark-object subtraction "further developed to calculate a haze thickness map" for inhomogeneous haze; tested on WorldView-2 | **Partly**: the closest VHR haze-thickness method. Single date, multispectral |
| 3, greyscale | He et al. 2013 (full text, §3.5 and Fig. 8) | The local linear model "is more likely to be valid in the RGB color space than in gray-scale"; a grey guide gives halos where an edge is not distinguishable in grey | A known handicap of our greyscale rule. The reference variant sidesteps the colour prior but not this |
| 3, greyscale | Tarel & Hautière 2009 (ICCV; major conference; abstract) | A fast visibility restoration that handles "both color images or gray level images" (atmospheric veil inference, restoration, smoothing, tone mapping) | Shows that grey-level dehazing is a recognised setting |
| 3, ω (none kept) | He et al. 2011 (§4.1) | ω = 0.95 keeps "a very small amount of haze for the distant objects"; "the value of ω is application based" | **Our own rule** (ω = 1 for analysis). Not argued against |
| **4. Airlight A: brightest pixel among the top 0.1% dark channel** | He et al. 2011 (§4.3) | "We first pick the top 0.1 percent brightest pixels in the dark channel … Among these pixels, the pixels with highest intensity in the input image I are selected"; this beats the brightest-pixel method, which can land on "a white car or a white building" | **Supported** (same as He) |
| 4, caveats | He et al. 2011 (§6, Discussion) | The method fails where scene objects are "inherently similar to the atmospheric light" (white marble), and "the constant-airlight assumption may be unsuitable when the sunlight is very influential" | Partly applies. My read: large white roofs, and the sunlit against shaded sides of a cumulus, are our cases |
| **5. t faded to 1 over 20 m past the gate** (linear in distance, 1 − d/40 px) | Zhu & Woodcock 2012; Zhu et al. 2015; Claverie et al. 2018 (RSE; 12.3; full text, §3.3.1) | Operational masks treat the near-cloud band as contaminated and remove it. LaSRC: "Adjacency cloud is applied over 150 m windows (i.e., five 30 m pixels with the window size selected empirically) surrounding cloudy pixels" | **Partly**: an edge band is standard. A fixed 20 m fade that removes only (1 − d/40) of the haze is **our own rule** |
| 5, the seam | Lin et al. 2013 (IEEE TGRS; 9.4; abstract); Li et al. 2019 (Remote Sensing; 4.3, narrow; WHU; abstract); Pérez, Gangnet & Blake 2003 (ACM TOG; 13.0 **(new)**, 2025 value via Wikipedia citing JCR; Microsoft Research, company; abstract) | Reference-based cloud filling is posed as a Poisson equation for "radiometric accuracy and consistency" (Lin). Li refines the mask "to ensure that the labeled cloud boundaries go through homogeneous areas … to ensure a seamless reconstruction", then a "residual correction based on global optimization". Poisson editing gives "seamless editing of image regions" (Pérez) | The experts' seam fix is gradient-domain or global, not a linear ramp. This is a fix we have not tried (§2) |
| **5b. No guided filter or soft matting** (`DARKREF_GUIDED = False`) | He et al. 2011 (§4.1–4.2) | Without refinement the transmission shows "halos and block artifacts"; after soft matting "the halos and block artifacts are suppressed" | **Not supported**: the method's authors require a refinement step (§3) |
| 5b | He et al. 2013 (§5, Fig. 16) | Guided-filter dehazing: max filter first, guide = the hazy image, r = 20 and ε = 10⁻³ on a 600 × 400 image. (The exponent's minus sign was lost in text extraction; the raw glyph is a minus.) | Our tested setting was r = 60, ε = 10⁻⁴, with no max filter first, so it was not He's recipe (§3) |
| 5b | He et al. 2013 (§5, Limitations) | The guided filter "may exhibit halos near some edges"; "Halos are unavoidable for local filters when the filters are forced to smooth some edges" | The refinement is not halo-free either. Edge-aware variants: Li et al. 2015 (WGIF; IEEE TIP; abstract) "can avoid halo artifacts" |
| **6. t < 0.2 left as is, "cannot assess"** | He et al. 2011 (§4.4) | J = (I − A) / max(t, t0) + A with "a typical value of t0 is 0.1", because where t is near 0 "the directly recovered scene radiance J is prone to noise" | **Supported** (a floor on t). Our 0.2, and abstaining rather than clamping, are our own stricter rule |
| 6 | Shen et al. 2015 (GRSM; full text, §VIII-A and §VIII-E) | Missing data is information "completely obscured or not observed". Thin cloud and haze are a different, "partially missing" kind. Temporal methods "are sensitive to land-cover changes, especially abrupt changes" | **Supported**: an opaque core is missing data; filling it from the before date copies pre-flood ground (also evidence 05) |
| 6 | Hänsch et al. 2022, SpaceNet 8 (CVPRW; Maxar, DLR and ORNL authors, company co-led; full text, evidence 08) | Analysts "were instructed to only attribute what was visible" under cloud | **Supported**: the labels themselves abstain |
| 6 | Portalés-Julià et al. 2023, WorldFloods v2 (Sci. Rep.; 4.9; abstract and evidence 02) | Water is segmented "even in areas covered by semitransparent clouds"; bright opaque cloud is left out of scoring | **Supported**: correct under thin cloud, abstain under thick cloud |
| 6, reporting | Zhu & Woodcock 2012 (p. 89) | Producer's accuracy matters more: "If clouds or cloud shadows are missed they will greatly undermine future analyses like change detection … if clear areas are masked … the only consequence is a little lost data" | **Supported**: when in doubt, abstain |

---

## 2. The ring fixes, ranked by literature support

The other agent's arms are a, b, c and d (`sn8_cloudedge.ARMS`). Fixes **N1–N3** are not on its list but come straight
from the sources. They are ranked together, by how directly an expert source backs each fix *in the form we would use
it*.

### 1. N1. Undo the minimum filter's erosion before using t (a max filter, i.e. an opening of the dark channel). Best supported, and not yet tested.
- **Source:** He, Sun & Tang 2013 (TPAMI; MSRA; full text, §5). Before guided filtering the raw transmission, "we first
  apply a max filter to counteract the morphological effects of the min filter (see [11])". He et al. 2011 (§4.1)
  gives the cause of the halo: "the transmission is not always constant in a patch".
- **Why it fits the ring (My read).** A 41 px minimum filter shrinks every bright (hazy) region by about half the window
  (about 10 m). Our box blur then spreads the edge over a further 41 px. So the haze edge in t, and the gate built from
  the same dark channel, sit inside the real cloud edge, and the outer band is under-corrected. A max filter of the same
  size puts the edge back.
- **Caveat:** the outermost thin fringe below the dark-rise cut stays outside the gate. N1 fixes the edge's *position*,
  not the fringe's *thickness* (that is arm a).

### 2. (a) A soft gate (hysteresis, connected to cloud blobs). Well supported in principle; correcting inside it is our extension.
- **For:**
  - Every operational mask dilates cloud because edges are thin cloud. Zhu et al. 2015 (RSE; full text) is the quote
    in "In short", item 2.
  - Zhu & Woodcock 2012 (full text) prefer commission to omission.
  - LaSRC uses 150 m adjacency windows (Claverie et al. 2018).
  - USGS Collection 2 QA_PIXEL has a "Dilated Cloud" bit (bit 1), and "Clear" requires both the cloud and dilated-cloud
    bits to be unset (USGS page, agency).
  - The Fmask software defaults to "Dilation size (in pixels) for cloud mask … 3" (GERSL README, v5.0).
  - The Google Earth Engine s2cloudless tutorial uses BUFFER, the "Distance (m) to dilate the edge of cloud-identified
    objects": 50 m, or 100 m for composites. It notes this raises commission. (Community tutorial, not official
    documentation.)
  - Hysteresis itself is Canny 1986 (TPAMI; full text, §VI). Points above a high threshold are kept, "as is the entire
    connected segment … which lies above a low threshold". This lowers both breaks and isolated false points.
  - A company patent does the cloud version: high-precision seeds grown into high-recall candidates connected to them
    (Guan et al., US 9,721,181 B2, The Climate Corporation; not peer-reviewed).
  - Google's Cloud Score+ argues that occlusion "is better treated as a regression problem rather than a discretized
    classification problem" (Pasquarella et al. 2023, CVPRW; Google; abstract). That supports a graded edge over a
    hard gate.
- **Limits:**
  - No JIF > 4 paper applies hysteresis to cloud masks. The support is the principle (Canny) plus operational
    dilation.
  - Operational systems **mask** the buffer; none corrects through it.
  - The newest Fmask README recommends *less* dilation (1 px for Landsat 8–9, 0 px for Sentinel-2) with its newer
    detectors. So the buffer size depends on how well the detector already reaches the edge.
  - Thin clouds "may have spectral signatures similar to the Earth surface underneath" (Zhu et al. 2015). That is why evidence 07's
    global hysteresis gate changed 3.7–26% of clear ground. Arm (a)'s "connected to the gate only" rule is the right
    guard.

### 3. (c) The guided filter on t, guided by the BEFORE image. The family is strongly supported; this guide is only partly.
- **For:**
  - Refinement is the method authors' own halo fix: soft matting (He 2011) and the guided filter (He 2013, TPAMI).
  - The guide "can be the input image itself or another different image" (He 2013, abstract), as in flash/no-flash
    denoising and joint upsampling.
- **Against this guide:**
  - The filter "can transfer the structures of the guidance image to the filtering output" (He 2013).
  - Joint/guided filters "directly transfer the structural information in the reference image to the target one …
    there may be completely different edges in the two images. Simply passing all patterns to the target could
    introduce significant errors" (Shen, Zhou, Xu & Jia 2015, ICCV; abstract).
  - Classic joint filtering "does not consider structural differences between guidance and input images" (Ham, Cho &
    Ponce 2018, TPAMI; abstract).
  - My read: between flood dates the structures differ by design. A before-image guide imprints pre-event edges into t,
    and so into the corrected after image. That is a bias toward "no change".
- **Better-supported forms:**
  - He's recipe: max filter first (N1), the hazy after image as the guide, and a larger ε (which smooths more and copies
    less texture).
  - Mutual structure (Shen et al. 2015), which uses only the structure both images share.
  - Weighted GIF (Li et al. 2015, TIP; abstract): "can avoid halo artifacts".
- **Caveats:**
  - He 2013 warns that a grey guide gives halos where edges are not distinct in grey.
  - Our earlier test (guide = after, r 60, ε 10⁻⁴, no max filter) flattened detail. That is consistent with strong
    structure transfer at a small ε (My read). It was not a test of He's recipe.

### 4. (b) A data-driven fade (t from the data past the gate). Partly supported.
- **For:**
  - The band's width is an empirical choice even in operational products: LaSRC's 150 m window was "selected
    empirically" (Claverie et al. 2018).
  - NASA's studies measure near-cloud contamination against distance from the nearest cloud and find it decays
    gradually: about 15 km at MODIS scale, "stronger … near optically thicker clouds and … near illuminated cloud sides"
    (Várnai & Marshak 2009, GRL; abstract).
  - Clouds are surrounded by "a belt of forming and evaporating cloud fragments and hydrated aerosols extending tens of
    kilometers" (Koren et al. 2007, GRL; abstract).
  - Wen et al. (2007, JGR-Atmospheres; 3.4, aggregator, **below the threshold**; NASA-led; abstract; context only)
    studied the effect with collocated MODIS and ASTER images. ASTER's visible bands are 15 m, which is my addition,
    not from the abstract. They call the cloud-induced enhancement "too large to be ignored".
  - So a fade fitted to the measured haze excess against distance follows how the experts measure the effect.
- **Limits:**
  - These are atmospheric studies at 250 m–1 km pixels, not dehazing methods. At 0.5 m their km-scale effect means a
    whole tile may sit inside the twilight zone (My read).
  - No dehazing paper was found that fits the fade from the data.

### 5. N2. Seamless (gradient-domain or global) blending where the correction stops. Supported for reference-based cloud filling; untested for haze.
- **Sources:** Lin et al. 2013 (TGRS; Poisson equation, global optimisation), Li et al. 2019 (Remote Sensing 4.3,
  narrow; boundaries through homogeneous areas, then residual correction), Pérez et al. 2003 (TOG; Microsoft Research).
- **Fit:** these replace thick cloud with another date's pixels, which our rule forbids. The transferable part is
  making the *correction field* (1 − t, or L) continuous at its border, instead of tapering it linearly. That is an
  analogy, not a tested haze method.

### 6. (d) A smaller dark-channel window near edges. Weakest support among top-venue sources.
- **For:**
  - He et al. 2011 (§4.5) show the trade-off themselves. A smaller patch weakens halos, but the prior "is less accurate
    for a small patch, and the recovered scene radiance is oversaturated", whereas "if the patch size is too large,
    halos near depth edges may become stronger".
  - My read: our reference variant does not rely on the prior. J's dark channel is measured from the before image, so
    the cost of a small window is mainly noise and misregistration (about 0.6 m), not invalidity. This makes (d) more
    defensible for us than for He.
- **Against:**
  - Adaptive-window dark-channel papers found here are in venues below the bar (IEEE Access, MDPI Applied Sciences,
    Sensors and Materials), so they are not cited.
  - The top-venue edge-aware alternatives avoid the patch altogether: a boundary constraint with weighted L1
    regularisation (Meng et al. 2013, ICCV; abstract), or the median operation that "can avoid halo effects" (Gibson,
    Vo & Nguyen 2012, IEEE TIP; abstract).

### 7. N3. Flag the edge band instead of (or as well as) correcting it. The operational default.
- **Sources:** Fmask, LaSRC, USGS C2 and Earth Engine all remove the dilated band from use. Fmask's stated reason is
  that missed cloud "will greatly undermine future analyses like change detection".
- **For us:** roads in the band could be "corrected, low confidence", reported separately (risk–coverage), or set
  aside if a fix does not pass its guards.

---

## 3. What we do that the literature argues against

1. **No refinement of t.**
   - He et al. (2011) name halos and block artefacts as the "main problems" of the raw transmission. Their method is
     raw t *plus* soft matting (2011) or the guided filter (2013).
   - Running without refinement predicts exactly the ring.
   - We turned refinement off for a measured reason (detail 0.68 against 1.04), but with a setting that differs from
     He's recipe (next item).
2. **A minimum filter with no max filter, plus a box blur.**
   - He 2013 explicitly counteracts the minimum filter's morphological effect before refining.
   - Our `dark_channel` keeps the erosion, and adds a 41 px box blur that He does not use.
   - Both move or soften the haze edge, inward and over about 20 m (My read).
3. **A fixed 20 m linear fade with no measured basis.**
   - The operational band widths are empirical (LaSRC) or user-set (Fmask).
   - Atmospheric studies show contamination falling off gradually over much longer distances.
   - Nothing published supports removing exactly (1 − d/40) of the haze.
4. **Fitting the tone curve on all clear pixels, flood included, starting 10 m from the gate.**
   - Normalisation experts fit on invariant (no-change) pixels (Schott 1988; Du 2002; Canty & Nielsen 2008; Nielsen
     2007).
   - Shen et al. (2015) note that histogram-based gap filling struggles in heterogeneous landscapes, and that temporal
     replacement "may result in an aliasing phenomenon" from registration errors and abrupt land-cover change.
   - Near-cloud pixels are themselves hazy (Zhu et al. 2015; Koren 2007; Várnai & Marshak 2009).
   - My read: the curve absorbs some flood darkening and some near-cloud haze. Evidence 07's changed-ground check on 12
     tiles found no measurable harm, at low power.
5. **The guided filter as tested** (a grey guide, a small ε, and no max filter) differs from He 2013 on three counts.
   He 2013 warns against the first (a grey guide, Fig. 8); the other two are departures from the published recipe.
   Its failure is therefore not evidence against the published method.

Nothing found argues against steps 3 (the haze model), 4 (the airlight) or 6 (abstaining under opaque cloud).

---

## 4. Gaps: what no expert source covers
- A dark channel taken from a co-registered clear *reference date* in place of the prior, on single-band VHR. Closest:
  Lin et al. 2015 (reference images), Hagolle 2010/2015 (multi-temporal, CNES) and Makarau 2014 (VHR haze thickness,
  DLR).
- Correcting *inside* a dilated cloud buffer. Every operational system masks it instead.
- Hysteresis used for cloud masks in a JIF > 4 journal. The support is Canny 1986 plus a company patent.
- Halo or ring artefacts at *cloud* edges in satellite dehazing, in a top venue. The halo literature is computer vision
  (depth edges); the near-cloud literature is atmospheric (MODIS scale).

---

## 5. References (DOIs checked against Crossref, 2026-10-25)

Authors as in the Crossref record; more than three authors are given as the first three plus "et al.".

| # | Reference | Venue basis | Read |
|---|---|---|---|
| 1 | Canny, J. (1986). A computational approach to edge detection. *IEEE TPAMI* PAMI-8(6), 679–698. https://doi.org/10.1109/TPAMI.1986.4767851 | TPAMI 18.6 (2024 value) | Full text (disk) |
| 2 | Canty, M. J., & Nielsen, A. A. (2008). Automatic radiometric normalization of multitemporal satellite imagery with the iteratively re-weighted MAD transformation. *Remote Sensing of Environment* 112(3), 1025–1036. https://doi.org/10.1016/j.rse.2007.07.013 | RSE 12.3 | Full text (disk) |
| 3 | Claverie, M., Ju, J., Masek, J. G., et al. (2018). The Harmonized Landsat and Sentinel-2 surface reflectance data set. *Remote Sensing of Environment* 219, 145–161. https://doi.org/10.1016/j.rse.2018.09.002 | RSE 12.3; NASA-led | Full text (disk), §3.3 |
| 4 | Du, Y., Teillet, P. M., & Cihlar, J. (2002). Radiometric normalization of multitemporal high-resolution satellite images with quality control for land cover change detection. *Remote Sensing of Environment* 82(1), 123–134. https://doi.org/10.1016/S0034-4257(02)00029-9 | RSE 12.3 | Abstract (evidence 05) |
| 5 | Gibson, K. B., Vo, D. T., & Nguyen, T. Q. (2012). An investigation of dehazing effects on image and video coding. *IEEE Transactions on Image Processing* 21(2), 662–673. https://doi.org/10.1109/TIP.2011.2166968 | TIP 13.7 (2024 value) | Abstract |
| 6 | Hagolle, O., Huc, M., Villa Pascual, D., & Dedieu, G. (2010). A multi-temporal method for cloud detection, applied to FORMOSAT-2, VENµS, LANDSAT and SENTINEL-2 images. *Remote Sensing of Environment* 114(8), 1747–1755. https://doi.org/10.1016/j.rse.2010.03.002 | RSE 12.3; CNES/CESBIO | Abstract via a search summary only |
| 6b | Hagolle, O., Huc, M., Villa Pascual, D., & Dedieu, G. (2015). A multi-temporal and multi-spectral method to estimate aerosol optical thickness over land, for the atmospheric correction of FormoSat-2, LandSat, VENμS and Sentinel-2 images. *Remote Sensing* 7(3), 2668–2691. https://doi.org/10.3390/rs70302668 | Remote Sensing 4.3 (narrow); CNES/CESBIO | Abstract (multi-temporal method "assumes that the surface reflectances are stable with time"; degraded for "a very quick variation of landscape") |
| 7 | Ham, B., Cho, M., & Ponce, J. (2018). Robust guided image filtering using nonconvex potentials. *IEEE TPAMI* 40(1), 192–207. https://doi.org/10.1109/TPAMI.2017.2669034 | TPAMI 18.6 (2024 value) | Abstract |
| 8 | Hänsch, R., Arndt, J., Lunga, D., et al. (2022). SpaceNet 8 – The detection of flooded roads and buildings. *CVPRW 2022*, 1471–1479. https://doi.org/10.1109/CVPRW56347.2022.00153 | CVPRW; Maxar co-authors | Full text (evidence 08) |
| 9 | He, K., Sun, J., & Tang, X. (2011). Single image haze removal using dark channel prior. *IEEE TPAMI* 33(12), 2341–2353. https://doi.org/10.1109/TPAMI.2010.168 | TPAMI 18.6 (2024 value); Sun at MSRA | Full text (author copy) |
| 10 | He, K., Sun, J., & Tang, X. (2013). Guided image filtering. *IEEE TPAMI* 35(6), 1397–1409. https://doi.org/10.1109/TPAMI.2012.213 | TPAMI 18.6 (2024 value); He and Sun at Microsoft Research Asia (company) | Full text (author copy) |
| 11 | Koren, I., Remer, L. A., Kaufman, Y. J., et al. (2007). On the twilight zone between clouds and aerosols. *Geophysical Research Letters* 34(8), L08805. https://doi.org/10.1029/2007GL029253 | GRL 5.0 **(new; aggregator only, confirm in JCR)**; NASA GSFC | Abstract |
| 12 | Li, Z., Shen, H., Cheng, Q., et al. (2019). Thick cloud removal in high-resolution satellite images using stepwise radiometric adjustment and residual correction. *Remote Sensing* 11(16), 1925. https://doi.org/10.3390/rs11161925 | Remote Sensing 4.3 (narrow) | Abstract |
| 13 | Li, Z., Zheng, J., Zhu, Z., et al. (2015). Weighted guided image filtering. *IEEE Transactions on Image Processing* 24(1), 120–129. https://doi.org/10.1109/TIP.2014.2371234 | TIP 13.7 (2024 value) | Abstract |
| 14 | Lin, C.-H., Tsai, P.-H., Lai, K.-H., et al. (2013). Cloud removal from multitemporal satellite images using information cloning. *IEEE TGRS* 51(1), 232–241. https://doi.org/10.1109/TGRS.2012.2197682 | TGRS 9.4 | Abstract |
| 15 | Lin, C.-H., Lin, B.-Y., Lee, K.-Y., et al. (2015). Radiometric normalization and cloud detection of optical satellite images using invariant pixels. *ISPRS J. Photogramm. Remote Sens.* 106, 107–117. https://doi.org/10.1016/j.isprsjprs.2015.05.003 | ISPRS 12.9 | Abstract via a search summary (NASA MODIS publications page) |
| 16 | Makarau, A., Richter, R., Müller, R., et al. (2014). Haze detection and removal in remotely sensed multispectral imagery. *IEEE TGRS* 52(9), 5895–5905. https://doi.org/10.1109/TGRS.2013.2293662 | TGRS 9.4; DLR | Abstract |
| 17 | Meng, G., Wang, Y., Duan, J., et al. (2013). Efficient image dehazing with boundary constraint and contextual regularization. *ICCV 2013*, 617–624. https://doi.org/10.1109/ICCV.2013.82 | ICCV | Abstract |
| 18 | Nielsen, A. A. (2007). The regularized iteratively reweighted MAD method for change detection in multi- and hyperspectral data. *IEEE Transactions on Image Processing* 16(2), 463–478. https://doi.org/10.1109/TIP.2006.888195 | TIP 13.7 (2024 value) | Abstract |
| 19 | Pasquarella, V. J., Brown, C. F., Czerwinski, W., et al. (2023). Comprehensive quality assessment of optical satellite imagery using weakly supervised video learning. *CVPRW 2023*, 2125–2135. https://doi.org/10.1109/CVPRW59228.2023.00206 | Google-led (company) | Abstract |
| 20 | Pérez, P., Gangnet, M., & Blake, A. (2003). Poisson image editing. *ACM Transactions on Graphics* 22(3), 313–318. https://doi.org/10.1145/882262.882269 | TOG 13.0 **(new; Wikipedia citing JCR)**; Microsoft Research (company) | Abstract |
| 21 | Portalés-Julià, E., Mateo-García, G., Purcell, C., et al. (2023). Global flood extent segmentation in optical satellite images. *Scientific Reports* 13, 20316. https://doi.org/10.1038/s41598-023-47595-7 | Sci. Rep. 4.9 | Abstract; evidence 02 |
| 22 | Schott, J. R., Salvaggio, C., & Volchok, W. J. (1988). Radiometric scene normalization using pseudoinvariant features. *Remote Sensing of Environment* 26(1), 1–16. https://doi.org/10.1016/0034-4257(88)90116-2 | RSE 12.3 | Metadata (cited by #2) |
| 23 | Shen, H., Li, X., Cheng, Q., et al. (2015). Missing information reconstruction of remote sensing data: A technical review. *IEEE Geoscience and Remote Sensing Magazine* 3(3), 61–85. https://doi.org/10.1109/MGRS.2015.2441912 | GRSM 13.7 | Full text (author manuscript, WHU) |
| 24 | Shen, X., Zhou, C., Xu, L., & Jia, J. (2015). Mutual-structure for joint filtering. *ICCV 2015*, 3406–3414. https://doi.org/10.1109/ICCV.2015.389 | ICCV | Abstract |
| 25 | Skakun, S., Wevers, J., Brockmann, C., et al. (2022). Cloud Mask Intercomparison eXercise (CMIX): An evaluation of cloud masking algorithms for Landsat 8 and Sentinel-2. *Remote Sensing of Environment* 274, 112990. https://doi.org/10.1016/j.rse.2022.112990 | RSE 12.3; CEOS (agencies and companies) | Abstract |
| 26 | Tarel, J.-P., & Hautière, N. (2009). Fast visibility restoration from a single color or gray level image. *ICCV 2009*, 2201–2208. https://doi.org/10.1109/ICCV.2009.5459251 | ICCV | Abstract |
| 27 | Várnai, T., & Marshak, A. (2009). MODIS observations of enhanced clear sky reflectance near clouds. *Geophysical Research Letters* 36(6), L06807. https://doi.org/10.1029/2008GL037089 | GRL 5.0 **(new; aggregator only)**; NASA GSFC | Abstract |
| 28 | Wen, G., Marshak, A., Cahalan, R. F., et al. (2007). 3-D aerosol-cloud radiative interaction observed in collocated MODIS and ASTER images of cumulus cloud fields. *Journal of Geophysical Research: Atmospheres* 112(D13). https://doi.org/10.1029/2006JD008267 | JGR-A 3.4 **(new; aggregator) → below the threshold; context only** | Abstract |
| 29 | Zhang, Y., Guindon, B., & Cihlar, J. (2002). An image transform to characterize and compensate for spatial variations in thin cloud contamination of Landsat images. *Remote Sensing of Environment* 82(2–3), 173–187. https://doi.org/10.1016/S0034-4257(02)00034-2 | RSE 12.3 | Secondary (Fmask's account, pp. 84–85); needs blue and red, so not used for greyscale |
| 30 | Zhu, Z., & Woodcock, C. E. (2012). Object-based cloud and cloud shadow detection in Landsat imagery. *Remote Sensing of Environment* 118, 83–94. https://doi.org/10.1016/j.rse.2011.10.028 | RSE 12.3 | Full text (disk) |
| 31 | Zhu, Z., Wang, S., & Woodcock, C. E. (2015). Improvement and expansion of the Fmask algorithm: Cloud, cloud shadow, and snow detection for Landsats 4–7, 8, and Sentinel 2 images. *Remote Sensing of Environment* 159, 269–277. https://doi.org/10.1016/j.rse.2014.12.014 | RSE 12.3 | Full text (author copy) |
| 32 | Qiu, S., Zhu, Z., & He, B. (2019). Fmask 4.0: Improved cloud and cloud shadow detection in Landsats 4–8 and Sentinel-2 imagery. *Remote Sensing of Environment* 231, 111205. https://doi.org/10.1016/j.rse.2019.05.024 | RSE 12.3 | Metadata (the author PDF exceeded the fetch limit) |

**Not peer-reviewed (operational practice):**
- USGS, *Landsat Collection 2 Quality Assessment Bands*: https://www.usgs.gov/landsat-missions/landsat-collection-2-quality-assessment-bands
  (read: bit 1 "Dilated Cloud"; Clear = cloud and dilated-cloud bits unset; dilation size not stated).
- GERSL, *Fmask* software README, v5.0: https://github.com/GERSL/Fmask (read: cloud 3 / shadow 5 / snow 0 px defaults;
  Fmask-UPL recommends 1 px for Landsat 8–9 and 0 px for Sentinel-2).
- Google Earth Engine community tutorial, *Sentinel-2 Cloud Masking with s2cloudless* (author jdbcode):
  https://developers.google.com/earth-engine/tutorials/community/sentinel-2-s2cloudless (read: BUFFER 50 m, or 100 m
  for composites).
- Guan, W., Khadka, P., & Gerard, J. (2017). *Cloud detection on remote sensing imagery*. US Patent 9,721,181 B2, The
  Climate Corporation: https://patents.google.com/patent/US9721181B2/en (description read, first part only; claims not
  read).

**Impact-factor notes (new this session):**
- **GRL 5.0** and **JGR-Atmospheres 3.4** come only from journalmetrics.org; AGU's statistics page returned 403.
- **ACM TOG 13.0** comes from Wikipedia citing JCR 2025; ACM's page returned 403.
- Confirm all three in JCR at GMU. Pérez 2003 qualifies anyway as company-led (Microsoft Research). Wen 2007 does not
  qualify and is context only.

---

## 6. Needs GMU login (paywalled; most useful first)
1. Lin et al. 2015, ISPRS JPRS, https://doi.org/10.1016/j.isprsjprs.2015.05.003 . The closest published match to our
   reference-based correction; read how invariant pixels and reference images are built.
2. Hagolle et al. 2010, RSE, https://doi.org/10.1016/j.rse.2010.03.002 . The multi-temporal cloud test in full, and
   whether MAJA dilates its mask (the ATBD at theia-land.fr reset the connection).
3. Makarau et al. 2014, TGRS, https://doi.org/10.1109/TGRS.2013.2293662 . How the haze-thickness map handles haze
   edges on WorldView-2.
4. Zhang, Guindon & Cihlar 2002, RSE, https://doi.org/10.1016/S0034-4257(02)00034-2 . The HOT removal step (only the
   detection side was read, through Fmask).
5. Lin et al. 2013, TGRS, https://doi.org/10.1109/TGRS.2012.2197682 . The Poisson seam treatment in full.
6. Li, Zheng, Zhu et al. 2015, TIP, https://doi.org/10.1109/TIP.2014.2371234 , and Gibson et al. 2012, TIP,
   https://doi.org/10.1109/TIP.2011.2166968 . Halo-free alternatives in full.
7. Koren et al. 2007 and Várnai & Marshak 2009, GRL (AGU; may be free after embargo). Distance profiles of near-cloud
   haze, for arm (b).
8. Du et al. 2002 and Schott et al. 1988, RSE. Invariant-pixel normalisation in full.

**Open, but not read here (blocked or too large for the fetch tool; no login needed):**
- Fmask 4.0 author PDF (gerslab.cahnr.uconn.edu, over 10 MB).
- CMIX PDF (NTRS 20220006382, or roderic.uv.es, which returned 403).
- Li et al. 2019 (MDPI, 403).
- Cloud Score+ (CVF open access, 403).
- Meng 2013 and Shen 2015 (CVF open access, ICCV).
- Pérez 2003 (Microsoft Research copy).
- Ham et al. 2018 (arXiv).
