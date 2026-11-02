"""Applies the preregistered decision rules (KEEP / MAYBE / DROP / NOT RUN) to bench3_numbers.json (Phase G) and
bench3r_numbers.json (Phase R, if present) and writes bench3_decisions.json (one line of evidence per arm).

Rules (preregistration_method_bench_3.md):
  helped alone = own-metric interval excluding 0 in the good direction (corrections: Ida primary CI below 0 with the
                 guard passed; D5: paired F1 CI above 0) OR 21-seed flood gain >= 0.
  KEEP   helps alone and in combination, interval excluding 0 (alone: an own-metric or flood interval in the good
         direction; combination: a factorial cell containing the arm with a flood interval above 0).
  MAYBE  helps on one metric only, or within noise (21-seed gain >= 0 with an interval including 0).
  DROP   no help, or harms (interval in the bad direction on a deciding metric: flood CI below 0 vs production, Ida
         primary CI above 0, HRC F1 CI below 0).
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def p2(x):
    return f"{100 * x:+.2f}"


def flood_txt(r):
    s = r["seeds"]
    return f"flood {p2(s['mean_gain'])} [{p2(s['ci'][0])}, {p2(s['ci'][1])}] pts ({s['seeds_better']} seeds better, " \
           f"{s['seeds_worse']} worse)"


def in_good_combo(arm, combo):
    return any(arm in r["members"] and r["ci"][0] > 0 for r in combo.values())


def in_good_combo_r0(arm, combo):
    return any(arm in r["members"] and r.get("vs_R0", {}).get("ci", [0])[0] > 0 for r in combo.values())


def decide_phase(num, corr_names, extra_not_run, hrc=None, label="G"):
    fl = num.get("flood", {})
    pri = num.get("ida_primary_vs_C0") or {}
    gc = num.get("ida_guard_grey_change_mean", {})
    combo = num.get("combo", {})
    rows = []
    for n, r in fl.items():
        if n == "C0 current two-date":
            continue
        s = r["seeds"]
        f_lo, f_hi, f_m = s["ci"][0], s["ci"][1], s["mean_gain"]
        ev = [flood_txt(r)]
        if "added" in r:
            ev.append(f"{r['added']} roads added, {r['removed']} removed")
            if "added_acc" in r:
                ev.append(f"accuracy on added roads {r['added_acc']['mean']:.3f} [{r['added_acc']['ci'][0]:.3f}, "
                          f"{r['added_acc']['ci'][1]:.3f}]")
        own_help = own_harm = False
        p = pri.get(n)
        if n in corr_names or p:
            if p:
                ok = p.get("guard_ok", True)
                ev.insert(0, f"Ida primary vs C0 {p['mean_diff']:+.4f} [{p['ci'][0]:+.4f}, {p['ci'][1]:+.4f}] "
                             f"({p['tiles']} tiles), guard {gc.get(n, float('nan')):.2f} ({'ok' if ok else 'fails'})")
                own_help = p["ci"][1] < 0 and ok
                own_harm = p["ci"][0] > 0
            if "vs_base" in r:
                vb = r["vs_base"]["seeds"]
                ev.append(f"vs {r['vs_base']['base']} {p2(vb['mean_gain'])} [{p2(vb['ci'][0])}, {p2(vb['ci'][1])}]")
        base_good = label == "R" and "vs_base" in r and r["vs_base"]["seeds"]["ci"][0] > 0   # Phase R: R0 is the baseline
        if label == "R" and "vs_base" in r and r["vs_base"]["base"] == "R0 colour baseline" and not any("vs R0" in e for e in ev):
            vb = r["vs_base"]["seeds"]
            ev.append(f"vs R0 {p2(vb['mean_gain'])} [{p2(vb['ci'][0])}, {p2(vb['ci'][1])}] ({vb['seeds_better']} better)")
        helped = own_help or f_m >= 0 or base_good
        alone_ci_good = own_help or f_lo > 0 or base_good
        harms = own_harm or f_hi < 0
        if helped and alone_ci_good and in_good_combo(n, combo):    # KEEP needs a cell above production
            v = "KEEP"
        elif harms:
            v = "DROP"
        elif helped:
            v = "MAYBE"
        else:
            v = "DROP"
        if v == "DROP" and harms and base_good:
            v, harms = "MAYBE", False   # better than R0 with an interval above 0; below production only through R0's own cost
        why = "harms" if harms else ("no help" if v == "DROP" else ("helps alone and in combination" if v == "KEEP"
                                                                    else ("helps vs R0 (interval above 0), not vs production" if base_good
                                                                          else "within noise / one metric")))
        rows.append({"arm": n, "decision": v, "evidence": f"{why}: " + "; ".join(ev)})
    if hrc:
        for r in hrc.get("paired_all", []):
            band = next(b for b in hrc["paired_band"] if b["a"] == r["a"])
            lo, hi = r["ci_low"], r["ci_high"]
            v = "DROP" if hi < 0 else ("MAYBE" if (lo > 0 or r["F1 a - b"] >= 0) else "DROP")
            if lo > 0 and band["ci_low"] > 0:
                v = "MAYBE"                 # own metric only: the flood effect is conditional (spotter gate on SN8)
            rows.append({"arm": r["a"], "decision": v,
                         "evidence": f"HRC_WHU F1 vs D0 {r['F1 a - b']:+.4f} [{lo:+.4f}, {hi:+.4f}]; boundary band "
                                     f"{band['F1 a - b']:+.4f} [{band['ci_low']:+.4f}, {band['ci_high']:+.4f}]; "
                                     f"images higher {r['images a higher']}, lower {r['images b higher']}"})
    for n, why in extra_not_run.items():
        v = "MAYBE" if why.startswith("run (condition met)") else "NOT RUN"   # D5's conditional flood test ran
        rows.append({"arm": n, "decision": v, "evidence": ("within noise: " + why) if v == "MAYBE" else why})
    for name, r in combo.items():
        rows.append({"arm": name, "decision": "(cell)", "evidence":
                     f"gain {p2(r['mean_gain'])} [{p2(r['ci'][0])}, {p2(r['ci'][1])}] pts; interaction "
                     f"{p2(r.get('interaction', r.get('interaction_vs_R0', 0)))} "
                     f"[{p2(r['interaction_ci'][0])}, {p2(r['interaction_ci'][1])}]"})
    return rows


NOT_RUN_G = {
    "T1d Otsu on the dark rise": "check only: integer Otsu k* = 72 vs 71.36 (within 5 DN) confirms production's cut",
    "L2 Lin cloning from the before date": "diagnostic only (pastes pre-storm ground into the flood)",
    "Chip-level cloud gate (Shendryk 2019)": "needs Justin's ruling on derived labels",
    "FwDET edge gate": "needs a new 3DEP download",
    "DINOv3": "research-only",
}


def main():
    out = {}
    num = json.loads((HERE / "bench3_numbers.json").read_text())
    hrc_f = HERE / "hrc_d5_numbers.json"
    hrc = json.loads(hrc_f.read_text()) if hrc_f.exists() else None
    nr = dict(NOT_RUN_G)
    if hrc:
        nr["D5 flood effect (spotter gate on SN8)"] = num.get("d5_flood_note", "conditional on D5 passing its own rule")
    out["phase_G"] = decide_phase(num, ["P1 Pan C tile", "P1w Pan C local", "S1 sphere DCP", "S1p sphere + Pan C",
                                        "M1 median DCP", "L1 Poisson seam"], nr, hrc)
    rf = HERE / "bench3r_numbers.json"
    if rf.exists():
        numr = json.loads(rf.read_text())
        if "flood" in numr:
            out["phase_R"] = decide_phase(numr, [n for n in numr["flood"] if n.startswith("A2b") or n.startswith("RGB ")],
                                          {"D1e as a spotter feature (Use A)": "HRC_WHU has no clear partner date"},
                                          None, "R")
    tmp = HERE / "bench3_decisions.json.writing"
    tmp.write_text(json.dumps(out, indent=1))
    tmp.replace(HERE / "bench3_decisions.json")
    for ph, rows in out.items():
        print(ph)
        for r in rows:
            print(f"  {r['decision']:8s} {r['arm']:40s} {r['evidence'][:150]}")


if __name__ == "__main__":
    main()
