# Repository-wide instructions for agentic scientific work

## Purpose

This repository supports agentic GeoAI research exercises. Agents may propose scientific questions,
hypotheses, methods, data sources, analyses, critiques, and revisions.

## Scientific rules

1. Separate **evidence** from **inference**.
2. Never invent citations, datasets, measurements, or results.
3. State uncertainty and unresolved assumptions explicitly.
4. Do not treat agreement between two LLM agents as independent scientific validation.
5. Prefer falsifiable/testable research questions over vague topics.
6. For geospatial work, explicitly consider scale, CRS, spatial dependence, temporal alignment,
   sampling bias, spatial leakage, MAUP/ecological fallacy where relevant, and external validity.
7. Proposed methods must identify how the central claim could be wrong.
8. A reviewer must assess the underlying evidence, not only prose quality.
9. Human approval is required before claiming scientific novelty, causal inference, policy relevance,
   or external validity.
10. Preserve intermediate artifacts so the research trajectory can be audited.

## Shared research state

Agents should treat files in `inputs/` as source material and files in `outputs/` as evolving state.
Do not modify original input evidence.

## Output discipline

Each agent must:
- identify inputs used;
- state assumptions;
- provide a structured output;
- identify unresolved issues;
- suggest the next scientific action.
