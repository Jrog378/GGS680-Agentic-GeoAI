#!/usr/bin/env python3
"""Week 5 multi-agent lab / Assignment 3: build agent prompt packets from one fill-in form.

Run (no arguments needed, from anywhere):
    python Claude/05_Project/run.py

Everything you type by hand lives in lab_inputs.ipynb (created on first run if it is missing).
Each run reads that form plus the agent outputs already saved in outputs/, then:
  1. prints the status of the 8 stages (done / ready / waiting / locked / stale);
  2. writes a prompt packet for every stage whose inputs exist (old packets are cleared first),
     and keeps the packet each saved output was made from in outputs/packets_used/;
  3. tells you which packet to paste into a new agent chat and where the agent must save its answer;
  4. lists the form fields that are due now and checks your reference list.

A finished stage turns "stale" when an output it used changed, or when the form fields it was
built from changed (topic, references, evidence, decisions, notes).

Options (all optional):
    --form PATH          form to read (default: lab_inputs.ipynb next to this script; a .md form also works)
    --redo N             move stage N's output and its packet to outputs/history/, rebuild it as a revision
    --copy               copy the next packet to the clipboard
    --evidence-chars N   max characters embedded per evidence file (default: 20000)
    --accept             treat every saved output as up to date (clears stale flags after a change
                         that doesn't matter, e.g. fixing a typo in the form)
    --rebuild-form       regenerate the form layout from this script, keeping your answers
                         (the old form is backed up to outputs/history/)

No model is called. This is the course's manual orchestrator (week5/run.py) made form-driven.
Standard library only; pypdf is used for PDF evidence if it is installed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_FORM = HERE / "lab_inputs.ipynb"
OUTPUTS = HERE / "outputs"
PACKETS = OUTPUTS / "prompt_packets"
USED = OUTPUTS / "packets_used"
HISTORY = OUTPUTS / "history"
SIGNATURES = OUTPUTS / ".signatures.json"
EVIDENCE = HERE / "evidence"
PLACEHOLDER = "*(your answer)*"
HINT = "> 💡"
TEXT_SUFFIXES = {".md", ".txt", ".csv", ".json", ".geojson", ".tex", ".py", ".yaml", ".yml", ".html"}
MIN_REFERENCES, MIN_REFERENCE_YEAR = 5, 2023
COURSE_EXAMPLE_A1 = ("How can GeoAI help us understand and anticipate the effects of drought on inland "
                     "waterway transportation and freight-system resilience?")


def find_repo_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / ".git").exists():
            return p
    return start


REPO = find_repo_root(HERE)


def show(p: Path) -> str:
    """Path relative to the repo root (what the agent chat sees), else absolute."""
    try:
        return p.resolve().relative_to(REPO).as_posix()
    except ValueError:
        return str(p)


# --------------------------------------------------------------------------------------------
# The form: every manual entry, in the order you need it
# --------------------------------------------------------------------------------------------

@dataclass
class Field:
    code: str
    title: str
    hint: str
    default: str = ""
    private: bool = False   # 🔒 never sent to an agent
    due: int = 0            # nag once this many stages are done
    optional: bool = False  # never nag
    template: bool = False  # default is a scaffold; leaving it unchanged counts as blank
    track: bool = True      # editing it marks stages built from it as stale


def notes_field(n: int, agent: str) -> Field:
    return Field(f"N{n}", f"Notes for Agent {n} — {agent}",
                 "Optional. Anything this agent should know or do differently; sent verbatim.",
                 optional=True, due=n - 1)


REFERENCE_TEMPLATE = "Author et al. (Year). Title. Journal. DOI:"

PARTS = [
    ("Part 1 — Your topic, references and evidence",
     "Assignment 3: a GeoAI problem you want to write a paper on. Fill this in before Agent 1; it goes to "
     "every agent. If you change it later, finished stages are marked stale.",
     [
         Field("A1", "Broad research problem",
               "Your own topic, kept broad. Leave room for the agents to reason; don't specify a method.",
               default=COURSE_EXAMPLE_A1),
         Field("A2", "Boundary conditions",
               "Constraints every question and method must respect.",
               default="- The problem must contain a meaningful spatial component.\n"
                       "- The investigation should be achievable with public or research-accessible data.\n"
                       "- The aim is to produce a testable research question, not merely a descriptive "
                       "mapping exercise.\n"
                       "- The methodology must contain an explicit validation strategy.\n"
                       "- The paper must be completable and submittable to a peer-reviewed journal within "
                       "eight weeks, using AI-assisted coding and analysis."),
         Field("A3", "Your domain notes",
               "Optional. Candidate study area, sensors/imagery, constraints, datasets you already know.",
               optional=True),
         Field("A4", "Evidence",
               "Optional. Paste text here. A line that is just a file path (e.g. literature/paper.pdf) "
               "embeds that file. Files in Claude/05_Project/evidence/ are embedded automatically.",
               optional=True),
         Field("L1", "References you have read and verified",
               f"Assignment 3 needs at least {MIN_REFERENCES} peer-reviewed papers from "
               f"{MIN_REFERENCE_YEAR}–2026. One per line; tick [x] only after you have read it and checked "
               "year, venue and DOI. Put the PDFs in evidence/ so the agents can read them. Agents may cite "
               "only these.",
               default="\n".join(f"- [ ] {REFERENCE_TEMPLATE}" for _ in range(MIN_REFERENCES)),
               template=True),
     ]),
    ("Part 2 — Before you run any agent",
     "🔒 For you only, and optional for Assignment 3. X2 is good evidence of your own thinking for the "
     "critical-review slide.",
     [
         Field("X1", "Exercise: rules versus roles",
               "Open AGENTS.md and one file in agents/.",
               default="1. A rule that applies to all agents:\n"
                       "2. An instruction unique to the specialist (which role file?):\n"
                       "3. A capability the specialist does not currently have:",
               private=True, template=True, optional=True),
         Field("X2", "Exercise: pre-register your intuition",
               "Kept private so it can't bias the agents. Compared with the agent's question in X4.",
               default="- My best research question:\n"
                       "- Expected direction of the effect/pattern:\n"
                       "- A result that would surprise me:",
               private=True, template=True, optional=True),
     ]),
    ("Part 3 — Agents 1–2: three refined research questions",
     "Run Agent 1, then the critic. Log what you accept, change or reject in H1 (add N1 instructions if you "
     "like), then run `python Claude/05_Project/run.py --redo 1` to get three refined questions. Then "
     "critique the three yourself (H2) and select one (H3).",
     [
         notes_field(1, "Research Question Agent"),
         Field("X3", "Exercise: inspect the first packet",
               "Open outputs/prompt_packets/01_research_question_agent.md.",
               default="- Role:\n- Goal:\n- Evidence/state supplied:\n- Required output:\n"
                       "- Missing tools/evidence:\n"
                       "- Is this agent autonomous yet, or am I still orchestrating it by hand?",
               private=True, template=True, optional=True),
         Field("X4", "Exercise: your question versus the agent's",
               "Compare X2 with the agent's best candidate in outputs/research_questions.md.",
               default="- More testable:\n- More specific:\n- More interesting:\n"
                       "- More vulnerable to data limitations:",
               private=True, template=True, optional=True, due=1),
         notes_field(2, "Scientific Critic"),
         Field("H1", "Decision log: AI suggestions you accepted, changed or rejected",
               "Keep adding rows through every stage. This is the 'critical human review' evidence (20% of "
               "the grade). Sent to later agents so they don't re-propose what you rejected.",
               default="| Stage | AI suggestion | Accepted / changed / rejected | Why |\n"
                       "|---|---|---|---|\n| | | | |",
               template=True, track=False, due=2),
         Field("H2", "Your critique of the three refined questions",
               "Your own assessment of each question, for the slides. 🔒 Not sent to agents.",
               default="\n\n".join(
                   f"**Q{i}:**\n- Scientific value (my critique):\n"
                   f"- Feasibility in eight weeks (my critique):\n"
                   f"- Origin: AI as-is / AI edited by me / my own" for i in (1, 2, 3)),
               private=True, template=True, due=2),
         Field("H3", "Selected question, hypothesis and scope",
               "What every later agent works from.",
               default="- Selected question (final wording):\n- Why it is the strongest of the three:\n"
                       "- Main hypothesis:\n- Scope (study area, time period, unit of analysis):",
               template=True, due=2),
     ]),
    ("Part 4 — Agent 3: abstract, contribution and the human checkpoint",
     "Agents 4–8 stay locked until every box in H4 is ticked.",
     [
         notes_field(3, "Writer (abstract + contribution)"),
         Field("X5", "Exercise: claim audit",
               "Quote sentences from outputs/abstract_v1.md.",
               default="- An observation/background claim:\n- A proposed-method sentence:\n"
                       "- An expected-contribution sentence:\n- Any sentence masquerading as a result?",
               private=True, template=True, optional=True, due=3),
         Field("H4", "Human checkpoint",
               "Change [ ] to [x] only when it is true. This unlocks Agents 4–8.",
               default="- [ ] I critiqued all three questions myself (H2) and selected one (H3)\n"
                       "- [ ] Main hypothesis and scope approved\n"
                       f"- [ ] At least {MIN_REFERENCES} recent peer-reviewed references read and verified (L1)\n"
                       "- [ ] Abstract checked: no fabricated findings or citations",
               template=True, track=False, due=3),
     ]),
    ("Part 5 — Journal target and co-author (you, not the agents)",
     "Agents are told never to state an impact factor or name a real person, so these come from you.",
     [
         Field("H5", "Journal target",
               "Journal Impact Factor must be > 3. Look it up yourself. Sent to the writer to frame the "
               "contribution for the journal's scope.",
               default="- Journal:\n- Journal Impact Factor (> 3):\n"
                       "- Metric year and source (e.g. 2025 JIF, Clarivate JCR / journal website):\n"
                       "- Why the paper fits the journal's scope:",
               template=True, due=3),
         Field("H6", "Possible co-author (subject matter expert)",
               "A possible collaborator, not a claim they have agreed. 🔒 Not sent to agents.",
               default="- Name:\n- Affiliation:\n- Relevant expertise:\n"
                       "- Scientific content checks they could provide:",
               private=True, template=True, due=3),
     ]),
    ("Part 6 — Agents 4–5: methodology, eight-week plan and critique",
     "Agent 4 designs the method and the eight-week work plan; Agent 5 checks whether they can support the "
     "inference. To revise after the critique, fill H7 and run `python Claude/05_Project/run.py --redo 4`.",
     [
         notes_field(4, "Methodology Agent"),
         notes_field(5, "Methodology Critic"),
         Field("H7", "Your decisions on the methodology critique",
               "After reading outputs/methodology_review.md. Goes to Agents 4 (on redo), 6, 7. "
               "Log the same decisions in H1.",
               default="- Critiques I accept (and what should change):\n"
                       "- Critiques I reject or qualify, and why:",
               template=True, due=5),
         Field("X6", "Exercise: map question → evidence",
               "Fill in the right-hand column.",
               default="| Element | Your study |\n|---|---|\n| Research question | |\n"
                       "| Unit of analysis | |\n| Outcome/target | |\n| Main explanatory variable | |\n"
                       "| Key spatial dependence | |\n| Baseline/comparator | |\n"
                       "| External validation source | |\n"
                       "| What would falsify/weaken the hypothesis? | |",
               private=True, template=True, optional=True, due=5),
     ]),
    ("Part 7 — Agent 6: data, access and AI-assisted tools",
     "Anything the agent can't verify should come back marked TO VERIFY.",
     [
         notes_field(6, "Data + Tool Agent"),
         Field("X7", "Exercise: tool or agent?",
               "Tool = deterministic capability (geopandas.sjoin, a STAC search). "
               "Agent = goal-directed reasoning that selects/adapts actions.",
               default="- Item from outputs/data_tool_plan.md:\n- Tool or agent?\n- Why:",
               private=True, template=True, optional=True, due=6),
     ]),
    ("Part 8 — Agent 7: validation", "",
     [
         notes_field(7, "Validation Agent"),
         Field("X8", "Exercise: three levels of confidence",
               "If all three statements are identical, you are probably overclaiming.",
               default="- The agent has generated:\n- The workflow has verified:\n"
                       "- The evidence has validated/supported:",
               private=True, template=True, optional=True, due=7),
     ]),
    ("Part 9 — Agent 8 (optional): close the loop",
     "Not required for Assignment 3; useful for a future-work slide.",
     [
         notes_field(8, "Next-question agent"),
         Field("X9", "Final exercise: draw your system",
               "Mark 🧑 human approve/reject, 🛠️ tool used, ✅ evidence checked, 🔁 revision.",
               default="```text\nSTATE → AGENT → ACTION → NEW STATE → EVALUATION → NEXT ACTION\n```\n\n"
                       "- 🧑 Human approved/rejected:\n- 🛠️ Tool used:\n- ✅ Evidence checked:\n"
                       "- 🔁 Revision:\n"
                       "- Exit question: what would I automate next, and what would I keep visible?",
               private=True, template=True, optional=True, due=8),
     ]),
]

FIELDS = {f.code: f for _, _, fields in PARTS for f in fields}
CHECKPOINT = "H4"

FORM_INTRO = """# Week 5 lab / Assignment 3 — fill-in form

This is the only file you type in. `python Claude/05_Project/run.py` reads it on every run and builds the
agent prompt packets from it.

- 🤖 = sent to the agents inside their prompt packets
- 🔒 = for you only; never sent to an agent
- Replace *(your answer)* or fill in the scaffold under each heading. Lines starting with `> 💡` are hints and are ignored.
- Keep the codes in the headings (A1, H3, X5 …): the script finds each field by its code.

Fill it top to bottom as you go. Each run of the script lists the fields that are due."""


def md_cell(text: str) -> dict:
    lines = text.split("\n")
    return {"cell_type": "markdown", "id": uuid.uuid4().hex[:8], "metadata": {},
            "source": [l + "\n" for l in lines[:-1]] + [lines[-1]]}


def write_form(path: Path, keep: dict[str, str] | None = None) -> None:
    """Write the form; answers in `keep` (by code) replace the defaults."""
    cells = [md_cell(FORM_INTRO)]
    for title, intro, fields in PARTS:
        cells.append(md_cell(f"## {title}" + (f"\n\n{intro}" if intro else "")))
        for f in fields:
            tag = "🔒" if f.private else "🤖"
            cells.append(md_cell(f"### {f.code}. {f.title} {tag}\n\n{HINT} {f.hint}"))
            cells.append(md_cell((keep or {}).get(f.code) or f.default or PLACEHOLDER))
    nb = {"cells": cells, "metadata": {"language_info": {"name": "markdown"}},
          "nbformat": 4, "nbformat_minor": 5}
    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def read_form(path: Path) -> dict[str, str]:
    """Return {code: text} for every field heading found in the form (.ipynb markdown cells or .md)."""
    if path.suffix == ".ipynb":
        nb = json.loads(path.read_text(encoding="utf-8"))
        text = "\n\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown")
    else:
        text = path.read_text(encoding="utf-8")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)

    values: dict[str, str] = {}
    code, buf, fence = None, [], False
    for line in text.splitlines() + ["# end"]:
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence and re.match(r"#{1,3}\s", line):
            if code:
                values[code] = "\n".join(buf).strip()
            m = re.match(r"#{1,3}\s+([A-Z]\d+)\.\s", line)
            code = m.group(1) if m and m.group(1) in FIELDS else None
            buf = []
        elif code and not line.lstrip().startswith(HINT) and line.strip() != PLACEHOLDER:
            buf.append(line)
    return values


def norm(s: str) -> str:
    return " ".join(s.split())


def filled(code: str, values: dict[str, str]) -> str:
    """The field's text if the user has filled it in, else ''."""
    f, v = FIELDS[code], values.get(code, "")
    if f.template and norm(v) == norm(f.default):
        return ""
    return v


def checkpoint_passed(values: dict[str, str]) -> bool:
    boxes = re.findall(r"^\s*[-*]\s+\[([ xX])\]", values.get(CHECKPOINT, ""), flags=re.M)
    return bool(boxes) and all(b in "xX" for b in boxes)


def references(values: dict[str, str]) -> list[tuple[bool, str]]:
    """(verified, text) for each real entry in L1; untouched template lines are skipped."""
    out = []
    for line in values.get("L1", "").splitlines():
        m = re.match(r"\s*[-*]\s+\[([ xX])\]\s*(.*)", line)
        if m and m.group(2).strip() and m.group(2).strip() != REFERENCE_TEMPLATE:
            out.append((m.group(1) in "xX", m.group(2).strip()))
    return out


def references_block(values: dict[str, str]) -> str:
    refs = references(values)
    if not refs:
        return ""
    return "\n".join(f"- ({'read and verified by the human' if ok else 'NOT yet verified'}) {t}"
                     for ok, t in refs)


def old_references(values: dict[str, str]) -> list[str]:
    old = []
    for _, text in references(values):
        m = re.search(r"\b(?:19|20)\d{2}\b", text)
        if m and int(m.group()) < MIN_REFERENCE_YEAR:
            old.append(text[:60])
    return old


def problem_block(values: dict[str, str]) -> str:
    return "\n\n".join([
        "# Broad research problem", filled("A1", values) or "(not provided)",
        "## Initial boundary conditions", filled("A2", values) or "(none)",
        "## Human notes", filled("A3", values) or "(none)",
    ])


# --------------------------------------------------------------------------------------------
# Stages: role + task + which state each agent receives
# --------------------------------------------------------------------------------------------

@dataclass
class Stage:
    num: int
    name: str
    role: str
    task: str
    output: str
    packet: str
    deps: tuple = ()      # outputs that must exist first (also used for staleness)
    extras: tuple = ()    # outputs included if present (e.g. reviewer feedback on a redo)
    fields: tuple = ()    # human decisions/notes from the form sent with this stage
    gated: bool = False   # needs the human checkpoint
    optional: bool = False
    revision: str = ("Address the feedback, keep what still holds, and finish with a short list of what "
                     "you changed.")


STAGES = [
    Stage(1, "Research Question Agent", "research_question_agent.md",
          "Generate and rank 3–5 candidate GeoAI research questions and hypotheses. Each must be answerable "
          "in a paper completed and submitted within eight weeks.",
          "research_questions.md", "01_research_question_agent.md",
          extras=("question_review.md",), fields=("H1", "N1"),
          revision="Produce exactly THREE refined questions that respond to the critique and to the human's "
                   "decision log (H1). Do not re-propose anything the human rejected. For each question, "
                   "say what changed from the previous version and why."),
    Stage(2, "Scientific Critic", "scientific_critic.md",
          "Critique the candidate research questions, including feasibility for an eight-week paper. "
          "Recommend the strongest question or request revision.",
          "question_review.md", "02_scientific_critic.md",
          deps=("research_questions.md",), fields=("H1", "N2")),
    Stage(3, "Writer", "writer.md",
          "Write a 200–300 word proposed-study abstract for the selected question (H3). Then add a "
          "'Contribution' section: for each reference in the human-verified list, one line on what it "
          "established and one on what the proposed work adds. If a journal target is given (H5), frame the "
          "contribution for its scope. Use proposal language ('we will test'), never results language.",
          "abstract_v1.md", "03_writer_abstract.md",
          deps=("research_questions.md", "question_review.md"), fields=("H3", "H5", "H1", "N3")),
    Stage(4, "Methodology Agent", "methodology_agent.md",
          "Design a GeoAI methodology that can test the selected hypothesis (H3), scoped to a paper that can "
          "be completed and submitted within eight weeks using AI-assisted coding and analysis. Cover data "
          "and access, study area and unit of analysis, analytical steps, a baseline/comparator, validation "
          "checks, spatial assumptions, key risks, and what evidence could weaken the claim. End with an "
          "eight-week work plan table (week, tasks, deliverable, main risk).",
          "methodology_v1.md", "04_methodology_agent.md",
          deps=("research_questions.md", "question_review.md", "abstract_v1.md"),
          extras=("methodology_review.md",), fields=("H3", "H7", "H1", "N4"), gated=True),
    Stage(5, "Methodology Critic", "scientific_critic.md",
          "Critique the methodology as a scientific reviewer, emphasizing spatial validity, falsifiability, "
          "and whether the eight-week work plan is realistic.",
          "methodology_review.md", "05_methodology_critic.md",
          deps=("methodology_v1.md", "research_questions.md"), fields=("H3", "N5"), gated=True),
    Stage(6, "Data + Tool Agent", "data_tool_agent.md",
          "Map the revised methodology to plausible datasets and computational tools, including the "
          "AI-assisted coding and analysis tools to be used: what each would do and what the human must "
          "check by hand. Mark anything uncertain TO VERIFY.",
          "data_tool_plan.md", "06_data_tool_agent.md",
          deps=("methodology_v1.md", "methodology_review.md"), fields=("H3", "H7", "H1", "N6"), gated=True),
    Stage(7, "Validation Agent", "validation_agent.md",
          "Design the validation plan and identify what evidence would support or falsify the main "
          "scientific claim.",
          "validation_plan.md", "07_validation_agent.md",
          deps=("research_questions.md", "methodology_v1.md", "data_tool_plan.md"),
          extras=("methodology_review.md",), fields=("H3", "H7", "H1", "N7"), gated=True),
    Stage(8, "Next question (optional)", "validation_agent.md",
          "Given the proposed methodology and its largest unresolved threat to validity, propose one "
          "follow-on research question that would most reduce scientific uncertainty. Name the threat, "
          "state the question and the hypothesis it tests, and say what result would change the current plan.",
          "next_question.md", "08_next_question.md",
          deps=("methodology_v1.md", "methodology_review.md", "validation_plan.md"),
          extras=("data_tool_plan.md",), fields=("H3", "N8"), gated=True, optional=True),
]


def digest(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]


def signature(s: Stage, values: dict[str, str], evidence: list) -> dict[str, str]:
    """Fingerprint of the form inputs a stage's packet is built from."""
    sig = {"A1–A3": digest(problem_block(values)), "L1": digest(references_block(values)),
           "evidence": digest("\n".join(f"{a}\n{b}" for a, b in evidence))}
    for code in s.fields:
        if FIELDS[code].track:
            sig[code] = digest(filled(code, values))
    return sig


def stage_status(s: Stage, checkpoint: bool, sig_now: dict, sig_saved: dict | None) -> tuple[str, str]:
    out = OUTPUTS / s.output
    missing = [d for d in s.deps if not (OUTPUTS / d).exists()]
    if out.exists():
        newer = [d for d in s.deps if d not in missing
                 and (OUTPUTS / d).stat().st_mtime > out.stat().st_mtime]
        if missing:
            return "stale", f"{missing[0]} is missing (being redone?)"
        if newer:
            return "stale", f"{newer[0]} changed after this was saved"
        changed = [k for k in sig_now if sig_saved and k in sig_saved and sig_saved[k] != sig_now[k]]
        if changed:
            return "stale", "form changed since this was saved: " + ", ".join(changed)
        return "done", ""
    if missing:
        return "waiting", "needs " + ", ".join(missing)
    if s.gated and not checkpoint:
        return "locked", f"tick every box in {CHECKPOINT}"
    return "ready", ""


# --------------------------------------------------------------------------------------------
# Evidence and packets
# --------------------------------------------------------------------------------------------

def as_existing_file(line: str) -> Path | None:
    s = line.strip().lstrip("-*").strip().strip("`'\"")
    if not s or len(s) > 400:
        return None
    for cand in (HERE / s, REPO / s, Path(s).expanduser()):
        try:
            if cand.is_file():
                return cand.resolve()
        except OSError:
            pass
    return None


def read_evidence_file(p: Path, limit: int) -> str:
    suffix = p.suffix.lower()
    try:
        if suffix in TEXT_SUFFIXES:
            text = p.read_text(encoding="utf-8", errors="replace")
        elif suffix == ".ipynb":
            nb = json.loads(p.read_text(encoding="utf-8"))
            text = "\n\n".join("".join(c["source"]) for c in nb["cells"])
        elif suffix == ".pdf":
            try:
                import logging
                from pypdf import PdfReader
                logging.getLogger("pypdf").setLevel(logging.ERROR)  # malformed-but-readable PDF chatter
            except ImportError:
                return "[PDF not embedded: pypdf is not installed. Attach the file to the chat yourself.]"
            text = "\n".join(page.extract_text() or "" for page in PdfReader(str(p)).pages)
        else:
            return f"[{suffix or 'binary'} file not embedded. Attach it to the chat yourself.]"
    except Exception as exc:  # unreadable file: say so in the packet instead of crashing
        return f"[Could not read this file: {exc}]"
    text = text.strip()
    if len(text) > limit:
        text = text[:limit] + f"\n\n[… truncated at {limit:,} of {len(text):,} characters]"
    return text or "[File is empty or has no extractable text.]"


def collect_evidence(values: dict[str, str], limit: int) -> list[tuple[str, str]]:
    files, pasted = [], []
    if EVIDENCE.exists():
        files += sorted(p.resolve() for p in EVIDENCE.rglob("*") if p.is_file()
                        and not any(part.startswith(".") for part in p.relative_to(EVIDENCE).parts))
    for line in filled("A4", values).splitlines():
        p = as_existing_file(line)
        (files if p else pasted).append(p or line)
    items = []
    if "\n".join(pasted).strip():
        items.append(("pasted into the form (A4)", "\n".join(pasted).strip()))
    seen = set()
    for p in files:
        if p not in seen:
            seen.add(p)
            items.append((show(p), read_evidence_file(p, limit)))
    return items


def latest_previous(s: Stage) -> Path | None:
    stem = Path(s.output).stem
    # only plain timestamped archives count (not __packet.md or other labelled copies)
    old = sorted(p for p in HISTORY.glob(f"{stem}__*.md")
                 if re.fullmatch(rf"{re.escape(stem)}__\d{{8}}-\d{{6}}\.md", p.name))
    return old[-1] if old else None


def build_packet(s: Stage, values: dict[str, str], evidence: list, rules: str) -> str:
    out_rel = show(OUTPUTS / s.output)
    role = (HERE / "agents" / s.role).read_text(encoding="utf-8").strip()

    task = s.task
    previous = latest_previous(s) if not (OUTPUTS / s.output).exists() else None
    if previous:
        task += ("\n\nThis is a REVISION. Your previous version is included under CURRENT RESEARCH STATE, "
                 "together with any reviewer feedback and human decisions. " + s.revision)

    human = []
    if s.gated:
        human.append(f"Human checkpoint {CHECKPOINT} passed: the human critiqued the candidate questions, "
                     "selected one, approved the hypothesis and scope, verified the references, and checked "
                     "the abstract for fabricated findings and citations.")
    for code in s.fields:
        v = filled(code, values)
        if v:
            human.append(f"## {code}. {FIELDS[code].title}\n\n{v}")

    state = [f"## FILE: research problem (form fields A1–A3)\n\n{problem_block(values)}"]
    for name in (*s.deps, *s.extras):
        p = OUTPUTS / name
        if p.exists():
            state.append(f"## FILE: outputs/{name}\n\n{p.read_text(encoding='utf-8').strip()}")
    if previous:
        state.append(f"## PREVIOUS VERSION OF YOUR OUTPUT: outputs/history/{previous.name}\n\n"
                     f"{previous.read_text(encoding='utf-8').strip()}")

    refs = references_block(values) or ("None supplied yet. Treat every literature, novelty and "
                                         "contribution claim as unverified.")
    ev = "\n\n".join(f"## EVIDENCE: {label}\n\n{text}" for label, text in evidence)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""# PROMPT PACKET — Stage {s.num} of {len(STAGES)}: {s.name}

> Generated by `{show(HERE / 'run.py')}` on {stamp} from `lab_inputs.ipynb` and `outputs/`.
> Do not edit this file; edit the form and rerun the script.

**Save your complete response as Markdown to `{out_rel}`** (path relative to the repository root).
If you cannot write files, return the complete Markdown and the human will save it.
Everything you need is in this packet.

# SHARED RULES (AGENTS.md)

{rules}

# AGENT ROLE

{role}

# CURRENT TASK

{task}

# HUMAN DECISIONS AND INSTRUCTIONS

{chr(10).join(chr(10) + h for h in human).strip() or "None recorded."}

# HUMAN-VERIFIED REFERENCES (L1)

{refs}

# CURRENT RESEARCH STATE

{chr(10).join(chr(10) + x for x in state).strip()}

# EVIDENCE

{ev or "No evidence files supplied."}

# EXECUTION REQUIREMENT

Work only from the supplied state and clearly label missing evidence.
Return the requested structured artifact. Do not silently change the research question.
Cite only the human-verified references or the supplied evidence; mark any other needed citation
[citation needed]. Never state a journal impact factor or name a real person as a possible collaborator.
"""


def copy_to_clipboard(text: str) -> bool:
    for cmd in (["pbcopy"], ["clip"], ["xclip", "-selection", "clipboard"]):
        if shutil.which(cmd[0]):
            subprocess.run(cmd, input=text.encode("utf-8"), check=False)
            return True
    return False


# --------------------------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--form", type=Path, default=DEFAULT_FORM)
    ap.add_argument("--redo", type=int, choices=range(1, len(STAGES) + 1), metavar="N")
    ap.add_argument("--copy", action="store_true")
    ap.add_argument("--evidence-chars", type=int, default=20000)
    ap.add_argument("--accept", action="store_true")
    ap.add_argument("--rebuild-form", action="store_true")
    args = ap.parse_args()
    run_py = show(HERE / "run.py")

    for d in (PACKETS, USED, HISTORY):
        d.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    if not args.form.exists():
        write_form(args.form)
        print(f"Created the form: {show(args.form)}\n")
    elif args.rebuild_form:
        old = read_form(args.form)
        keep = {c: filled(c, old) for c in old if filled(c, old)}
        backup = HISTORY / f"{args.form.stem}__{stamp}{args.form.suffix}"
        shutil.copy2(args.form, backup)
        write_form(args.form, keep)
        print(f"Rebuilt the form layout, kept your answers; old form backed up to {show(backup)}\n")

    if args.redo:
        s = STAGES[args.redo - 1]
        out = OUTPUTS / s.output
        if out.exists():
            dest = HISTORY / f"{out.stem}__{stamp}.md"
            shutil.move(str(out), str(dest))
            if (USED / s.packet).exists():
                shutil.move(str(USED / s.packet), str(HISTORY / f"{out.stem}__{stamp}__packet.md"))
            print(f"Redo stage {s.num}: moved {s.output} (and its packet) to {show(HISTORY)}/\n")
        else:
            print(f"Redo stage {s.num}: {s.output} doesn't exist yet, nothing to archive\n")

    values = read_form(args.form)
    missing_codes = [c for c in FIELDS if c not in values]
    checkpoint = checkpoint_passed(values)
    rules = (HERE / "AGENTS.md").read_text(encoding="utf-8").strip()
    evidence = collect_evidence(values, args.evidence_chars)
    saved = json.loads(SIGNATURES.read_text()) if SIGNATURES.exists() else {}

    if args.accept:
        base, accepted = time.time(), 0
        for i, s in enumerate(STAGES):  # re-stamp in stage order so no output looks older than its inputs
            out = OUTPUTS / s.output
            if out.exists():
                os.utime(out, (base + i, base + i))
                saved[s.output] = signature(s, values, evidence)
                accepted += 1
        print(f"Accepted {accepted} saved output(s) as up to date; stale flags cleared.\n")

    for old in PACKETS.glob("*.md"):
        old.unlink()

    rows, packets = [], {}
    for s in STAGES:
        sig_now = signature(s, values, evidence)
        status, why = stage_status(s, checkpoint, sig_now, saved.get(s.output))
        if all((OUTPUTS / d).exists() for d in s.deps) and (checkpoint or not s.gated):
            text = build_packet(s, values, evidence, rules)
            packets[s.num] = PACKETS / s.packet
            packets[s.num].write_text(text, encoding="utf-8")
            if status == "ready":  # the last packet written before the output appears is the one used
                (USED / s.packet).write_text(text, encoding="utf-8")
        if status == "ready" or (status == "done" and s.output not in saved):
            saved[s.output] = sig_now
        rows.append((s, status, why))
    SIGNATURES.write_text(json.dumps(saved, indent=1, ensure_ascii=False) + "\n")

    # ---- report
    refs = references(values)
    verified = sum(ok for ok, _ in refs)
    groups = {"A": "inputs", "H": "decisions", "N": "agent notes", "X": "exercises"}
    counts = []
    for letter, label in groups.items():
        codes = [c for c in FIELDS if c.startswith(letter) and c != CHECKPOINT]
        counts.append(f"{label} {sum(bool(filled(c, values)) for c in codes)}/{len(codes)}")
    print(f"Week 5 lab / Assignment 3 — {show(HERE)}")
    print(f"Form {show(args.form)}: " + " · ".join(counts))
    print(f"References (L1): {verified} verified of {len(refs)} listed (need {MIN_REFERENCES}) · "
          f"evidence items embedded: {len(evidence)} · checkpoint {CHECKPOINT} "
          f"{'passed' if checkpoint else 'not ticked'}\n")

    print(f" #  {'Agent':<26}{'Output':<24}Status")
    for s, status, why in rows:
        print(f" {s.num}  {s.name:<26}{s.output:<24}{status}{' — ' + why if why else ''}")

    nxt = next(((s, st, why) for s, st, why in rows if st != "done" and not s.optional), None)
    if nxt is None:
        nxt = next(((s, st, why) for s, st, why in rows if st != "done"), None)
        print("\nAll required stages are done." + (" Stage 8 is optional." if nxt else ""))
    print()
    if nxt is not None:
        s, st, why = nxt
        if st == "locked":
            print(f"NEXT: open the form and tick every box in {CHECKPOINT} (human checkpoint), then rerun. "
                  f"That unlocks stage {s.num}, {s.name}.")
        elif st == "stale":
            print(f"NEXT: stage {s.num} ({s.name}) is stale: {why}.\n"
                  f"      If that matters, rerun it:  python {run_py} --redo {s.num}\n"
                  f"      If it doesn't:              python {run_py} --accept")
        elif st == "waiting":
            print(f"NEXT: stage {s.num} is waiting: {why}.")
        else:
            packet = packets[s.num]
            print(f"NEXT: stage {s.num}, {s.name}"
                  + (" (revision: previous version included)" if latest_previous(s) else ""))
            print(f"  Paste into a NEW agent chat:\n"
                  f"    Follow {show(packet)} and save your response to {show(OUTPUTS / s.output)}.")
            if args.copy:
                ok = copy_to_clipboard(packet.read_text(encoding="utf-8"))
                print("  (full packet copied to the clipboard)" if ok else "  (no clipboard tool found)")

    done = 0
    for _, st, _ in rows:
        if st not in ("done", "stale"):
            break
        done += 1
    due = [f for f in FIELDS.values() if not f.optional and f.due <= done and not filled(f.code, values)]
    if due:
        print("\nFill in now (lab_inputs.ipynb): " + "; ".join(f"{f.code} {f.title}" for f in due))
    if nxt and nxt[1] == "ready":
        print(f"Optional before running it: N{nxt[0].num} notes for this agent.")

    warnings = []
    if norm(filled("A1", values)) == norm(COURSE_EXAMPLE_A1):
        warnings.append("A1 is still the course's example problem; Assignment 3 needs your own topic.")
    elif not filled("A1", values):
        warnings.append("A1 (research problem) is empty; the agents have nothing to work from.")
    if verified < MIN_REFERENCES:
        warnings.append(f"Only {verified} of the {MIN_REFERENCES} required references are ticked as read "
                        f"and verified in L1. Agents can't support novelty or contribution claims without them.")
    for t in old_references(values):
        warnings.append(f"L1 reference looks older than {MIN_REFERENCE_YEAR}: {t}…")
    if missing_codes:
        warnings.append(f"No heading found for {', '.join(missing_codes)} in the form. Keep "
                        f"'### <code>. <title>' headings intact, or run with --rebuild-form.")
    if warnings:
        print("\n" + "\n".join("Warning: " + w for w in warnings))


if __name__ == "__main__":
    main()
