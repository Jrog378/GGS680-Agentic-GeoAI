# GGS 662 — Agentic GeoAI Scientific Discovery Starter

This starter repository is designed for an advanced graduate class moving from **AI-assisted GIS** and
**autonomous geospatial workflows** toward **agentic scientific discovery**.

The central idea is that agents can contribute not only execution, but also:
- research-question generation;
- hypothesis formation and critique;
- methodology design;
- dataset/tool selection;
- scientific review;
- validation and revision;
- generation of follow-on research questions.

Humans remain scientific supervisors: they set scope, inspect evidence, challenge assumptions, approve
high-consequence decisions, and determine whether conclusions are scientifically defensible.

## Suggested class sequence

1. `05_01_agentic_geoai_scientific_discovery.ipynb`
   - conceptual framing;
   - scientific reasoning autonomy versus workflow autonomy;
   - research-question and hypothesis generation;
   - multi-agent critique;
   - methodology and evidence planning;
   - validation and human governance.

2. `05_02_multi_agent_geoai_lab.ipynb`
   - practical VS Code workflow;
   - inspect agent specifications;
   - generate a research question;
   - writer/reviewer loop;
   - methodology generation/review;
   - inspect state transitions;
   - run a small orchestrator in manual mode.

## Repository structure

```text
.
├── AGENTS.md
├── README.md
├── requirements.txt
├── 05_01_agentic_geoai_scientific_discovery.ipynb
├── 05_02_multi_agent_geoai_lab.ipynb
├── agents/
│   ├── research_question_agent.md
│   ├── scientific_critic.md
│   ├── writer.md
│   ├── methodology_agent.md
│   ├── data_tool_agent.md
│   └── validation_agent.md
├── inputs/
│   ├── problem.md
│   └── evidence/
├── outputs/
├── src/
│   ├── state.py
│   ├── prompts.py
│   └── orchestrator.py
└── run.py
```

## Two ways to use it

### A. Recommended for the first class: VS Code / Codex, human-visible orchestration

The Python code produces **prompt packets** from the role specifications and current research state.
Students paste/run those packets in separate agent conversations in VS Code and save the resulting
artifacts in `outputs/`.

This is deliberately transparent: students can see what each agent receives and what state changes.

### B. Later: automated orchestration

Replace the manual runner with a model/API adapter. Keep the same role specs, state representation,
output schemas, evaluation rules, and stopping conditions.

## Core teaching distinction

**More autonomy is not simply more automated code.**

A workflow agent may execute a researcher-defined pipeline autonomously.
A scientific-reasoning agent may instead propose questions, hypotheses, methods, evidence, or follow-on
experiments. These are different kinds of autonomy and require different evaluation.
