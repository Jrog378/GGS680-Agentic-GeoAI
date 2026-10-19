"""Training-free change map: cosine distance between DINOv3 (SAT-493M) patch features of a before/after pair."""
import os, sys, time
os.environ.setdefault("HF_HOME", "/Users/jusrogers/Masters/models/huggingface")  # keep weights in Masters/models

import numpy as np
import torch
import torch.nn.functional as F
import timm
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MODEL = "vit_large_patch16_dinov3.sat493m"
SIZE = 1024                        # 64 x 64 patches of 16 px
HERE = os.path.dirname(os.path.abspath(__file__))
SMOKE = os.path.join(HERE, "..", "smoke_test")
device = "mps" if torch.backends.mps.is_available() else "cpu"

t0 = time.time()
model = timm.create_model(MODEL, pretrained=True).eval().to(device)
cfg = timm.data.resolve_data_config({}, model=model)
print(f"loaded {MODEL} on {device} in {time.time() - t0:.1f}s; mean={cfg['mean']} std={cfg['std']}")

def load(name):
    img = Image.open(os.path.join(SMOKE, name)).convert("RGB").resize((SIZE, SIZE), Image.BICUBIC)
    x = torch.from_numpy(np.asarray(img)).permute(2, 0, 1).float() / 255
    x = (x - torch.tensor(cfg["mean"])[:, None, None]) / torch.tensor(cfg["std"])[:, None, None]
    return img, x

pre_img, pre = load("pre_2022-01-21.png")
post_img, post = load("post_2022-09-30.png")

t0 = time.time()
with torch.no_grad():
    feats = model.forward_features(torch.stack([pre, post]).to(device))   # (2, prefix + N, C)
feats = feats[:, model.num_prefix_tokens:, :]                               # drop CLS + register tokens
g = SIZE // 16
feats = F.normalize(feats, dim=-1).reshape(2, g, g, -1)
change = (1 - (feats[0] * feats[1]).sum(-1)).cpu().numpy()                 # cosine distance per patch
print(f"forward pass {time.time() - t0:.1f}s; grid {g}x{g}; change min/mean/max "
      f"{change.min():.3f}/{change.mean():.3f}/{change.max():.3f}")
np.save(os.path.join(HERE, "change_map.npy"), change)

fig, ax = plt.subplots(1, 3, figsize=(18, 6.4))
ax[0].imshow(pre_img); ax[0].set_title("Before (2022-01-21)")
ax[1].imshow(post_img); ax[1].set_title("After (2022-09-30)")
ax[2].imshow(post_img)
im = ax[2].imshow(np.kron(change, np.ones((16, 16))), cmap="inferno", alpha=0.55)
ax[2].set_title("DINOv3-SAT change (cosine distance)")
fig.colorbar(im, ax=ax[2], fraction=0.046)
for a in ax: a.axis("off")
fig.suptitle("Hurricane Ian, Fort Myers Beach: training-free change map", fontsize=14)
fig.tight_layout()
fig.savefig(os.path.join(HERE, "change_map.png"), dpi=90)
print("saved", os.path.join(HERE, "change_map.png"))
