"""Arm C1: He, Sun & Tang (2013, TPAMI 35:1397) section 5 dehazing recipe on our two-date t (handoff
literature_fulltext/he2013_guided_image_filtering_TPAMI.md section 5 p. 11; claim_checks_A He 2013 #1-2): each date's
dark channel as the 41 px minimum then 41 px maximum (an opening, "to counteract the morphological effects of the min
filter", no box blur), t as C0, then the guided filter on t guided by the hazy AFTER image on [0, 1], eps = 1e-3,
r = 55 px (He's r / patch = 20 / 15 scaled to our 41 px window); C0's 20 m fade. Uses sn8_cloudedge's "opened" t
source (imported).
"""
R, EPS = 55, 1e-3


def correct(before, after, valid, parts=None):
    from sn8_cloudedge import edge_dehaze, edge_parts
    parts = edge_parts(before, after, valid) if parts is None else parts
    if parts is None:
        return None
    return edge_dehaze(parts, before, after, valid, ("opened", R, EPS), ("fade",))
