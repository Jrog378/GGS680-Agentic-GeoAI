"""Copy the Week 3 routing and Week 4 audit evidence into the folders 04_02 names.

04_02 expects the evidence under the course repo root:
    outputs/week3_routing/                        original run (routes.gpkg, ..., routing_report.md)
    outputs/week3_routing/sensitivity_gap_25m/    required sensitivity rerun
    outputs/week3_routing/gap_tolerance_250m/     extra Week 3 rerun
    outputs/week4_validation/                     audit script, validation_table.csv, report, map

The working copies stay in Claude/03_Project and Claude/04_Project; this script only
copies them. Rerun it after any rerun of week3_routing.py or week4_audit.py so the
exported evidence matches.

Run:
    python export_evidence.py [--dest <repo root>/outputs]
"""

import argparse
import shutil
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
CLAUDE_DIR = SCRIPT_DIR.parent
REPO_ROOT = CLAUDE_DIR.parent
ROUTING_DIR = CLAUDE_DIR / "03_Project"

RERUNS = ["sensitivity_gap_25m", "gap_tolerance_250m"]
ROUTING_SCRIPTS = ["week3_routing.py", "plot_side_by_side.py"]


def copy_files(src_dir, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied = []
    for f in sorted(src_dir.iterdir()):
        if f.is_file() and not f.name.startswith("."):
            shutil.copy2(f, dest_dir / f.name)
            copied.append(f.name)
    return copied


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dest", default=str(REPO_ROOT / "outputs"),
                        help="destination outputs folder (default: <repo root>/outputs)")
    args = parser.parse_args()
    dest = Path(args.dest)

    week3 = dest / "week3_routing"
    report = {week3: copy_files(ROUTING_DIR / "outputs" / "default", week3)}
    for name in ROUTING_SCRIPTS:
        shutil.copy2(ROUTING_DIR / name, week3 / name)
        report[week3].append(name)
    for run in RERUNS:
        report[week3 / run] = copy_files(ROUTING_DIR / "outputs" / run, week3 / run)

    week4 = dest / "week4_validation"
    report[week4] = copy_files(SCRIPT_DIR / "outputs" / "week4_validation", week4)
    shutil.copy2(SCRIPT_DIR / "week4_audit.py", week4 / "week4_audit.py")
    report[week4].append("week4_audit.py")

    for folder, names in report.items():
        print(f"{folder.relative_to(dest.parent)}/  ({len(names)} files)")
        for n in names:
            print(f"    {n}")


if __name__ == "__main__":
    main()
