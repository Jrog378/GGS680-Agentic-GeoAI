import sys; sys.path.append("/Users/jusrogers/Masters/GGS662/ProjectBranch/ClaudeFunctions")
import numpy as np
from sn8_clouds import _tile, dark_channel, cloud_thresholds
from sn8_refhaze import _local_fit, _robust_global, REF_PASSES, REF_K, T_MIN
for T in ["2_19_55", "2_15_45"]:
    p, b, a, valid = _tile(T)
    b = np.where(valid, b, 0).astype(np.float32); a = np.where(valid, a, 0).astype(np.float32)
    rise = dark_channel(a, valid) - dark_channel(b, valid); thr = cloud_thresholds()["dark rise"]
    clear = valid & (rise <= thr)
    g, h = _robust_global(b[clear], a[clear], np.ones(int(clear.sum()), bool))
    x, y = b[clear].astype(float), a[clear].astype(float)
    # orthogonal (total least squares) slope, robust to noise in the before image
    C = np.cov(x, y); ev, evec = np.linalg.eigh(C); v = evec[:, 1]; g_tls = v[1] / v[0]
    r = np.corrcoef(x, y)[0, 1]
    w = valid.astype(np.float32)
    for _ in range(REF_PASSES):
        al, be = _local_fit(b, a, w); res = a - (al * b + be); s = 1.4826 * np.median(np.abs(res[w > 0])) + 1e-6
        w = (valid & (np.abs(res) < REF_K * s)).astype(np.float32)
    t = al / g; L = be - t * h
    cloud = valid & (rise > thr)
    print(T, f"clear share {clear.sum()/valid.sum():.2f}  OLS g={g:.3f} h={h:.1f}  TLS g={g_tls:.3f}  r={r:.2f}  sd before {x.std():.1f} after {y.std():.1f}")
    for nm, msk in (("cloud (dark rise)", cloud), ("clear", clear)):
        tt, LL = t[msk], L[msk]
        haze = (tt <= 1) & (tt >= T_MIN) & (LL >= 0)
        print(f"  {nm:18s} median alpha {np.median(al[msk]):.3f} t {np.median(tt):.2f} L {np.median(LL):.1f}  counted as haze {haze.mean():.2f}  t>1 {np.mean(tt>1):.2f}  L<0 {np.mean(LL<0):.2f}")
