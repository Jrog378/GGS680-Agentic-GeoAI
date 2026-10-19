"""Cut matching before/after crops from Maxar Open Data COGs (Hurricane Ian, Fort Myers Beach)."""
import os
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from rasterio.enums import Resampling
from pyproj import Transformer
from PIL import Image

os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN", "EMPTY_DIR")
os.environ.setdefault("GDAL_HTTP_MAX_RETRY", "5")      # S3 occasionally drops connections
os.environ.setdefault("GDAL_HTTP_RETRY_DELAY", "2")

BASE = "https://maxar-opendata.s3.amazonaws.com/events/Hurricane-Ian-9-26-2022/ard/17/031331321321"
SCENES = {
    "pre_2022-01-21": f"{BASE}/2022-01-21/10400100703E5500-visual.tif",
    "post_2022-09-30": f"{BASE}/2022-09-30/10300100DB06A700-visual.tif",
}
LON, LAT = -81.950, 26.452   # downtown Fort Myers Beach (Estero Island)
HALF_M = 450                 # 900 m x 900 m footprint
OUT_PX = 1536                # large enough for Gemma 4's 1120-token image budget

out_dir = os.path.dirname(os.path.abspath(__file__))
crops = {}
for name, url in SCENES.items():
    with rasterio.open(url) as src:
        x, y = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True).transform(LON, LAT)
        win = from_bounds(x - HALF_M, y - HALF_M, x + HALF_M, y + HALF_M, src.transform)
        arr = src.read([1, 2, 3], window=win, out_shape=(3, OUT_PX, OUT_PX),
                       resampling=Resampling.bilinear, boundless=True, fill_value=0)
        print(name, src.crs, "native gsd", round(src.res[0], 3), "->", round(2 * HALF_M / OUT_PX, 3), "m/px")
    img = Image.fromarray(np.moveaxis(arr, 0, -1).astype(np.uint8))
    img.save(os.path.join(out_dir, f"{name}.png"))
    crops[name] = img

# Side-by-side preview for a quick visual check
w = OUT_PX // 2
prev = Image.new("RGB", (2 * w + 10, w), "white")
for i, img in enumerate(crops.values()):
    prev.paste(img.resize((w, w)), (i * (w + 10), 0))
prev.save(os.path.join(out_dir, "preview_pair.png"))
print("saved to", out_dir)
