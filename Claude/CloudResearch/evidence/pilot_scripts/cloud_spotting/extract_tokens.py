"""Patch tokens of the 120 HRC_WHU development images, one image and one window at a time on the shared GPU.
    python3 -I extract_tokens.py v2     # DINOv2 (library, sn8_cloudspot.hrc_dinov2_tokens)
    python3 -I extract_tokens.py v3     # DINOv3 (research benchmark, dinov3_source.hrc_dinov3_tokens)
Prints shapes and timings only, no scores."""
import sys
import time

HERE = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/cloud_spotting"
sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
sys.path.append(HERE)

from sn8_cloudref import hrc_images

which = sys.argv[1]
if which == "v2":
    from sn8_cloudspot import hrc_dinov2_tokens as load
elif which == "v3":
    from dinov3_source import hrc_dinov3_tokens as load
else:
    raise SystemExit("usage: extract_tokens.py v2|v3")
names = hrc_images("train")
assert len(names) == 120, len(names)
t0 = time.time()
for k, name in enumerate(names):
    t = load(name)
    if k % 10 == 0 or k == len(names) - 1:
        print(f"{which} {k + 1}/{len(names)} {name} {t.shape} {t.dtype} {time.time() - t0:.0f} s", flush=True)
print(f"{which} done in {time.time() - t0:.0f} s", flush=True)
