"""Arm C2: IR-MAD invariant-pixel normalisation (Canty & Nielsen 2008, RSE 112:1025; handoff
literature_fulltext/canty2008_automatic_radiometric_normalization_irmad_RSE.md section 1, pp. 1027-1031;
claim_checks_A Canty #3, #6, #7) replacing C0's quantile tone curve.

On C0's clear pixels (every 4th for the iteration, as the paper's "representative subset"): CCA of the before and after
RGB (N = 3), MAD variates M_i = U_{N-i+1} - V_{N-i+1}, sigma_Mi^2 = 2 (1 - rho) from the re-weighted fit (Eq. 4),
Z = sum (M_i / sigma_Mi)^2, weights = Pr(no change) = 1 - chi2_3.cdf(Z) (Eq. 6), iterated until the canonical
correlations change by < 1e-4 (max 30). Invariant = clear pixels with Pr(no change) > 0.95. The before -> after grey map
= orthogonal regression on the invariant pixels (p. 1028). Abstain (the gate cannot be assessed) when fewer than
1,000 invariant pixels remain. QC as the paper (p. 1031): 30% of invariant pixels held out, paired t test of the means
and F test of the variances (reported only).
"""
import numpy as np
from scipy import linalg, stats

P_INV, MIN_INV, MAX_IT, TOL = 0.95, 1000, 30, 1e-4


def _weighted_cca(F, G, w):
    sw = w.sum()
    mf, mg = (w[:, None] * F).sum(0) / sw, (w[:, None] * G).sum(0) / sw
    Fc, Gc = F - mf, G - mg
    Sff = (w[:, None] * Fc).T @ Fc / sw
    Sgg = (w[:, None] * Gc).T @ Gc / sw
    Sfg = (w[:, None] * Fc).T @ Gc / sw
    N = F.shape[1]
    A = Sfg @ np.linalg.solve(Sgg, Sfg.T)
    vals, vecs = linalg.eigh(A, Sff)
    order = np.argsort(vals)[::-1]
    rho = np.sqrt(np.clip(vals[order], 0, 1))
    a = vecs[:, order]
    a /= np.sqrt(np.einsum("ij,jk,ki->i", a.T, Sff, a))[None, :]
    b = np.linalg.solve(Sgg, Sfg.T @ a) / np.maximum(rho, 1e-12)[None, :]
    b /= np.sqrt(np.einsum("ij,jk,ki->i", b.T, Sgg, b))[None, :]
    sgn = np.sign(np.einsum("ij,jk,ki->i", a.T, Sfg, b))
    b *= np.where(sgn == 0, 1, sgn)[None, :]
    return mf, mg, a, b, rho


def _z(F, G, mf, mg, a, b, rho):
    U, V = (F - mf) @ a, (G - mg) @ b
    M = U - V                                       # ordered by rho descending; the sum over i is order-free
    var = 2 * (1 - rho)
    return (M ** 2 / np.maximum(var, 1e-9)[None, :]).sum(1)


def irmad(F, G):
    w = np.ones(len(F))
    rho_old = None
    for it in range(MAX_IT):
        mf, mg, a, b, rho = _weighted_cca(F, G, w)
        w = 1 - stats.chi2.cdf(_z(F, G, mf, mg, a, b, rho), F.shape[1])
        if rho_old is not None and np.max(np.abs(rho - rho_old)) < TOL:
            break
        rho_old = rho
    return (mf, mg, a, b, rho), it + 1


def orthogonal_fit(x, y):
    mx, my = x.mean(), y.mean()
    _, _, vt = np.linalg.svd(np.stack([x - mx, y - my], 1), full_matrices=False)
    vx, vy = vt[0]
    slope = vy / vx if abs(vx) > 1e-12 else np.inf
    return float(slope), float(my - slope * mx)


def make_tone_fn(before_rgb, after_rgb, seed=662):
    """A tone_fn for c_common.darkref_variant (gamma 1): IR-MAD on the clear pixels' RGB, orthogonal grey fit."""
    def tone_fn(before, after, clear, valid, b, a):
        idx = np.flatnonzero(clear)
        sub = idx[::4]
        F = before_rgb.reshape(-1, 3)[sub].astype(np.float64)
        G = after_rgb.reshape(-1, 3)[sub].astype(np.float64)
        try:
            fit, its = irmad(F, G)
        except np.linalg.LinAlgError:
            return None, {"abstain": "IR-MAD failed (singular)", "invariant_px": 0}
        Fa = before_rgb.reshape(-1, 3)[idx].astype(np.float64)
        Ga = after_rgb.reshape(-1, 3)[idx].astype(np.float64)
        pnc = 1 - stats.chi2.cdf(_z(Fa, Ga, *fit), 3)
        inv = idx[pnc > P_INV]
        info = {"iterations": its, "rho": fit[4].tolist(), "invariant_px": int(len(inv)),
                "invariant_share_of_clear": float(len(inv) / max(len(idx), 1))}
        if len(inv) < MIN_INV:
            info["abstain"] = "invariant < 1000"
            return None, info
        rng = np.random.default_rng(seed)
        hold = rng.random(len(inv)) < 0.3
        x, y = b.ravel()[inv[~hold]].astype(np.float64), a.ravel()[inv[~hold]].astype(np.float64)
        slope, icpt = orthogonal_fit(x, y)
        if not np.isfinite(slope) or slope <= 0:
            info["abstain"] = f"orthogonal slope {slope}"
            return None, info
        xh, yh = b.ravel()[inv[hold]], a.ravel()[inv[hold]]
        pred = slope * xh + icpt
        if hold.sum() > 10:
            info["qc_t_p"] = float(stats.ttest_rel(pred, yh).pvalue)
            fstat = np.var(pred, ddof=1) / max(np.var(yh, ddof=1), 1e-9)
            df = hold.sum() - 1
            info["qc_f_p"] = float(2 * min(stats.f.cdf(fstat, df, df), 1 - stats.f.cdf(fstat, df, df)))
        info.update(slope=slope, intercept=icpt)
        return (lambda v: slope * np.asarray(v) + icpt), info
    return tone_fn


def correct(before, after, valid, before_rgb, after_rgb):
    from c_common import darkref_variant
    return darkref_variant(before, after, valid, tone_fn=make_tone_fn(before_rgb, after_rgb))
