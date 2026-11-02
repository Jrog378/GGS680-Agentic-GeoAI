"""DINOv3 as a token source for sn8_cloudspot.cross_validate: RESEARCH BENCHMARK ONLY, never part of the library.

Justin (2026-10-26): "we will not use dinov3 in the library, it is only for research and benchmarking our other
models". The tokens come from the other agent's research module, pilot_scripts/dinov3/dinov3_bench.tokens3:
timm vit_large_patch16_dinov3.sat493m, frozen, read offline, grey repeated to 3 channels, normalised with the
checkpoint's own mean and std, 2 x 2 windows, 16 px patches, class and register tokens dropped. Licence: Meta's
DINOv3 License (research use here only).

Tokens of the HRC_WHU development images are cached as float16 under ClaudeFunctions/.cache/cloudspot/ with a
research_ prefix (that folder is git-ignored). The cache key holds the source of tokens3 and its helpers as they were
when this module was imported, so an edit to dinov3_bench during a run cannot change the key mid-run.
"""
import hashlib
import inspect
import sys

FUNCS = "/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions"
DINOV3_DIR = "/Users/jusrogers/Masters/GGS662/Agentic-GeoAI/Claude/CloudResearch/evidence/pilot_scripts/dinov3"
for p in (FUNCS, DINOV3_DIR):
    if p not in sys.path:
        sys.path.append(p)

import numpy as np

from dinov3_bench import MODEL3, PATCH3, WINDOWS3, normalised3, tokens3, windows3
from sn8_cloudref import hrc_image
from sn8_cloudspot import CACHE_DIR, _key

SOURCE_HASH = [hashlib.sha256(inspect.getsource(f).encode()).hexdigest() for f in (tokens3, normalised3, windows3)]


def hrc_dinov3_tokens(name):
    """DINOv3 tokens (n_rows, n_cols, 1024) of one HRC_WHU development image's grey (every pixel valid), float16."""
    path = CACHE_DIR / f"research_hrc_dinov3_{name}_{_key([MODEL3, PATCH3, WINDOWS3, *SOURCE_HASH, name])}.npy"
    if not path.exists():
        im = hrc_image(name)
        t = tokens3(im["grey"], np.ones(im["grey"].shape, bool))
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        np.save(path, t.astype(np.float16))
    return np.load(path)


DINOV3 = (hrc_dinov3_tokens, PATCH3)
