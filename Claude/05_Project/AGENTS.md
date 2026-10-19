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

## Literature sourcing

When searching for or citing papers, use only reliable, peer-reviewed sources from reputable venues.

1. Journal articles must come from a journal with a Journal Impact Factor (JIF) of **at least 4.0**
   in the most recent Clarivate Journal Citation Reports release.
2. Record the journal's JIF, the JCR year, and the source of the figure next to each citation in the
   search report. If sources disagree, use the lower value. If the JIF cannot be confirmed, flag the
   paper as unverified instead of guessing.
3. Conference papers have no JIF. Accept them only from major peer-reviewed venues (e.g., CORE A*/A
   such as CVPR, ICCV, NeurIPS, ICLR, ACL), and label them as conference papers.
4. Do not cite preprints (arXiv, SSRN, etc.), predatory or unindexed journals, blogs, or workshop
   papers as evidence. A preprint may be cited only as the source of a dataset, and must be labelled
   as a preprint.
5. A paper that fails these rules but seems important should be listed separately for human review,
   not silently included or dropped.

## Shared research state

Agents should treat the human's form (`lab_inputs.ipynb`, embedded in each prompt packet) and files in
`evidence/` as source material, and files in `outputs/` as evolving state. Do not modify the form or the evidence.

## Output discipline

Each agent must:
- identify inputs used;
- state assumptions;
- provide a structured output;
- identify unresolved issues;
- suggest the next scientific action.
