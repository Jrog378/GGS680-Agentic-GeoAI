# 17: Independent truth for Ida under cloud: NOAA aerial photos, USGS high-water marks, 3DEP lidar (2026-10-29; feasibility check, metadata only)

**Why:** Justin (2026-10-29): "look further into the strongest combination suggestion", after evidence 16 showed that
SpaceNet 8's labels cannot score cloud removal ("to truly test this method we have to adopt a different dataset /
test area / study objective"). Nothing was downloaded except file headers and four small previews; sealed tiles were
not read.

**Our area:** development tiles, post image Maxar catalog `10300100C46F5900` (acquisition date to confirm; press
reports WorldView-2 "after" images on 31 Aug 2021). South scene 29.618–29.749 N, 89.934–90.028 W (105 tiles); west
scene 29.640–29.832 N, 90.041–90.140 W (121 tiles).

## 1. NOAA NGS emergency-response aerial photos (public domain; `s3://noaa-eri-pds/2021_Hurricane_Ida/`)
- 8 flights, 30 Aug – 2 Sep 2021; 3,953 GeoTIFF tiles of 45″ (about 1.2 km).
- 209 tiles touch our area (about 26 GB), from flights 20210830a, 20210830b, 20210831a and 20210902a.
- By tile outlines: 175 of 226 development tiles are at least 90% inside a photo tile; so are 49 of the 56 tiles with
  cloudy roads, carrying 230 of the 239 cloudy roads (84 thin, 146 opaque-tile) and all 24 trusted flooded roads under
  thin cloud. **These are upper bounds:** a photo tile's outline includes no-data (tile 0_13_5's best photo is mostly
  empty), so valid-pixel coverage still has to be measured.
- **Previews** (`figures/ida_noaa_check/`; left Maxar post, right NOAA photo): on 0_14_6, 0_14_5 and 0_14_7 the
  satellite tile is under thick cloud and the aerial photo shows roads, houses and fields clearly. Alignment needs
  checking (different sensor, view and resolution).

## 2. USGS high-water marks and storm-tide sensors (USGS STN, event 2021Ida)
- The Flood Event Viewer has an Ida event. The old web service (`stn.wim.usgs.gov/STNServices/...`) now redirects to
  the STN web page, so the Louisiana marks in our area were not counted. Next: the current STN download (Flood Event
  Viewer, apps.usgs.gov/fev) or the `pygeohydro` client.

## 3. USGS 3DEP lidar elevation, 1 m
- 52 DEM tiles over our area from two projects: LA_CoastalLouisiana_2020 (before Ida) and LA_2021GreaterNewOrleans
  (to confirm whether flown before or after Ida); about 10 GB in all, about 5 GB per project.

## What the combination would test
- **Clear view under the cloud:** the NOAA photo, 0–2 days from the satellite pass, is the reference for what the
  ground looked like. Measures: error of our de-hazed image against the photo inside the cloud gate (pixels and DINOv2
  features), He 2011 and no de-hazing as baselines, clear ground left unchanged as the guard; does the spotter's mask
  match where satellite and photo disagree; does CANNOT ASSESS fall where the photo shows ground we could not recover.
- **Water at each road, independent of the image:** high-water-mark water level minus lidar road elevation gives a
  physical flood depth per road. This is a derived label, which the "published labels, unmodified" rule does not yet
  allow: Justin's decision.

## Open items
- Valid-pixel coverage of the photos over the cloudy tiles; alignment of photo to satellite.
- The satellite acquisition date (catalog `10300100C46F5900`), to know the gap to each flight.
- High-water marks in our area (new STN endpoint).
- Downloads (about 26 GB photos, about 5–10 GB lidar) wait for Justin's OK and the external drive.
