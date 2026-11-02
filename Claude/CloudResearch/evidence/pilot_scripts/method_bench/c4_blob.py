"""Arm C4: the gate's minimum blob swept (0, 1,250, 5,000, 10,000 m^2; C0 = 2,500), as Fmask published the sensitivity
sweep that chose its constants (claim_checks_A g1 #1; claim_checks_C Fmask #6). C0's arithmetic otherwise."""
SIZES = (0.0, 1250.0, 5000.0, 10000.0)


def correct(before, after, valid, min_m2):
    from c_common import darkref_variant
    return darkref_variant(before, after, valid, min_m2=min_m2)
