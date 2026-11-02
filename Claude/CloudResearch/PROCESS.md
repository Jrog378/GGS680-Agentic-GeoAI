# How this research proposal was built (a reusable procedure)

Justin, 2026-10-23: "prompt me when needed and then go off and do your thing ... we are turning the pipeline into
something reusable not something that is going to need you to make all these changes every time I want to spin up a
project using it."

This file records the steps for the cloud research proposal, so the same procedure can start the next project. The
Assignment 3 workflow files stay where they are and are **not copied or edited**:
- `Agentic-GeoAI/Claude/05_Project/run.py` (stage list);
- `AGENTS.md` (scientific rules);
- `agents/*.md` (one role per stage).

A new project gets its own folder like this one, and Claude runs the stages as subagents from chat.

## Folder layout (one per project)
| Path | Holds | Who writes it |
|---|---|---|
| `input_card.md` | The problem in the human's words, scope, boundaries, domain notes, candidate references, human decisions | Claude drafts; the human corrects |
| `decision_log.md` | Every AI suggestion accepted, changed or rejected, with the human's words | Claude, after every human answer |
| `evidence/` | Measured results, literature summaries, checks, the research-question guide, pilot scripts | Claude (the coordinator); agents only read it |
| `outputs/` | Stage products: questions, critiques, abstract, methodology versions, data/tool plan, validation plan | The stage agents |
| `figures/` | Figures drawn by code from development data | Claude |
| `presentation/` | The deck workspace (deck-designer kit, local files) | Claude + the design kit |
| `PROCESS.md` | This record | Claude |

## Rules that held throughout
- **One human question at a time**, and only questions that need a human: rulings, rule exceptions, accounts,
  deletions, big downloads. Plain language, short sentences, a low reading level.
- **Evidence apart from inference** in every file (AGENTS.md rule 1). Agreement between agents is never validation.
- **Data:** development data only. Sealed pools stay unread until one logged check of a frozen setup.
- **Citations:** JIF ≥ 4, or company-led, or a major conference. Anything else is a method attribution. Every method
  on a slide is cited inline. A validation agent reads the papers before the deck is final.
- **Subagents** run one at a time per stage, in the background, with no forks. An earlier researcher agent spawned 10
  forks and had to be stopped.
- **Products are local files**, not artifacts (Justin, 2026-10-24: "use files in the CloudResearch folder not
  artifacts").

## Steps taken (2026-10-23 to 2026-10-24)
1. **Is it a research area?** Claude checked the literature on disk and measured the problem on development data
   (`evidence/01`, `02`). Justin: "lets take this idea and run with it".
2. **Input card.** Claude filled it from what was known. Justin rewrote the problem statement.
3. **Stages 1–2 (questions + critic):** five candidates and a critique (`outputs/research_questions.md`,
   `question_review.md`).
4. **Refinement with Justin, one question at a time** (three rounds; `research_questions_refined*.md`). Claude
   studied research-question craft and saved a checklist (`evidence/04_research_question_guide.md`). Justin chose the
   order Q2, Q3, Q1 and the wording of Q1 (`selected_questions.md`).
5. **Stage 3 (writer):** `abstract_v1.md`. Justin: "good for now, we are just creating the outline".
6. **Justin's ideas, tested as pilots on development data:**
   - two-date de-hazing (`ProjectBranch/ClaudeFunctions/sn8_refhaze.py`; scripts in `evidence/pilot_scripts/`);
   - the two-pass "scale and re-detect" design, backed by a literature search on reconstructing blocked pixels
     (`evidence/05`).
7. **Stage 4 (methodology) → Stage 5 (methodology critic, verdict REVISE) → methodology v2.** v2 maps every critic
   point (§21) and lists the decisions left for Justin (§19).
8. **Assignment 4 deck** (`presentation/`):
   - brief from the assignment's requirements;
   - Night Pass theme;
   - imagery panels and chart numbers drawn by code (`presentation/assets/panel_numbers.json`);
   - built by `presentation/build_slides.py`;
   - deckkit renumber, lint, render, then read every PNG;
   - PDF in `presentation/render/`;
   - a validation agent then checks every claim against the papers (`presentation/design/validation_report.md`).

   While drawing the slides, a label-free check showed the two-date fit is rough (evidence 01, methodology v2 before
   §6.4.6).
9. **Stage 6 (data + tool plan):** done 2026-10-24 → `outputs/data_tool_plan.md`. The deck's validation agent also
   ran (114 claims checked). Two sealed-label slips that day were logged in the data ledger. Lesson for the next
   project: name the development split in every agent prompt, forbid opening all-splits label folders, and take
   splits by name (`df, train, val, test, negative = split_tables()`).
10. **Still to do:**
    - Stage 7 (validation plan → `outputs/validation_plan.md`);
    - optional Stage 8 (next question);
    - Justin's open rulings (methodology v2 §19), one at a time;
    - the final product page in this folder.

## To start the next project with this procedure
1. Make a sibling folder of this one, with the layout above. Copy nothing from `05_Project/`.
2. Write the input card from what is known, and ask the human to rewrite the problem in their own words.
3. Run the stages in `run.py`'s order as background subagents. Each prompt names:
   - the role file (`05_Project/agents/<role>.md`);
   - `AGENTS.md`;
   - the project's input card, decision log, evidence and earlier outputs;
   - the stage's instruction (copied from `run.py`'s `STAGES`).
4. After each stage, bring the human only the decisions that need them, one at a time, and log every answer in
   `decision_log.md`.
5. Pilot the human's ideas on development data, and write the numbers into `evidence/` before any agent cites them.
6. For a talk, run the deck-designer kit on local files, with a validation agent before the deck is final.
