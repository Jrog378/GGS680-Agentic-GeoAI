"""Ida-reference helpers for bench 2: bench 1's run_ida functions imported read-only (usable_tiles, edge_r, cosdist,
patch_to_px, window_slices, PREP), plus a CPU-ONLY window_tokens (bench 1's picks MPS when the DINOv3 job has ended;
bench 2 never uses the GPU)."""
import hashlib

import numpy as np

import b2_common as B  # noqa: F401  (thread limits, sys.path)
from run_ida import PREP, cosdist, edge_r, patch_to_px, usable_tiles, window_slices  # noqa: F401  (bench 1, read-only)

_MODEL = {}
_TOK = {}


def model():
    if "m" not in _MODEL:
        import torch
        torch.backends.mps.is_available = lambda: False      # CPU only
        torch.set_num_threads(2)
        import sn8_dino as D
        m, dev = D.backbone()
        assert str(dev) == "cpu", f"bench 2 must not use a GPU device (got {dev})"
        _MODEL.update(m=m, dev=dev)
    return _MODEL["m"], _MODEL["dev"]


def windows_with(region, shape):
    from sn8_dino import PATCH
    _, _, wins = window_slices(shape)
    need = []
    for k, (r, c) in enumerate(wins):
        sl = (slice(r[0] * PATCH, (r[-1] + 1) * PATCH), slice(c[0] * PATCH, (c[-1] + 1) * PATCH))
        if region[sl].sum() > 0:
            need.append(k)
    return need


def window_tokens(grey, valid, need):
    """As bench 1's run_ida.window_tokens (same fill, normalisation and window split), on the CPU."""
    import torch
    from sn8_dino import MEAN, PATCH, STD
    m, dev = model()
    n_r, n_c, wins = window_slices(grey.shape)
    g = np.full((n_r * PATCH, n_c * PATCH), grey[valid].mean(), np.float32)
    g[: grey.shape[0], : grey.shape[1]] = np.where(valid, grey, grey[valid].mean())
    x = np.stack([(g / 255 - mu) / s for mu, s in zip(MEAN, STD)]).astype(np.float32)
    out = np.zeros((n_r, n_c, m.embed_dim), np.float32)
    for k in need:
        r, c = wins[k]
        win = x[:, r[0] * PATCH:(r[-1] + 1) * PATCH, c[0] * PATCH:(c[-1] + 1) * PATCH]
        h = hashlib.sha256(win.tobytes()).hexdigest()
        if h not in _TOK:
            with torch.inference_mode():
                f = m.forward_features(torch.from_numpy(win[None]).to(dev))[0, m.num_prefix_tokens:]
            _TOK[h] = f.float().cpu().numpy().reshape(len(r), len(c), -1)
        out[r[0]:r[-1] + 1, c[0]:c[-1] + 1] = _TOK[h]
    return out


def clear_tokens():
    _TOK.clear()
