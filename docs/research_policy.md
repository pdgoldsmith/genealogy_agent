# Genealogy Agent Research Policy

## Core principles

1. **Source over speculation**: hypotheses are allowed, conclusions require evidence.
2. **Record everything**: maintain an auditable log of resources, timestamps, and extraction steps.
3. **Cite claims**: each claim must include one or more source citations.
4. **Cross-check identity**: names alone are insufficient; validate by at least two additional attributes (date, place, relatives, occupation, etc.).
5. **Human-in-the-loop for ambiguity**: uncertain matches require explicit human acceptance.

## Session requirements

For every session, store:

- Research objective
- People/entities in scope
- Searches performed
- Assets examined (document/image/page identifiers)
- Extracted facts and confidence scores
- Contradictions and unresolved questions
- Human approvals/rejections

## Memory management rules

- Keep **working memory** concise and task-scoped.
- Move finalized facts into **verified memory** only after sufficient evidence.
- Keep **hypothesis memory** separate from verified facts.
- Do not overwrite contradictory facts; preserve provenance and status.

## Evidence confidence rubric

- **High**: primary source with direct identity corroboration.
- **Medium**: credible secondary source with partial corroboration.
- **Low**: single-source hint, weak transcription, or unresolved ambiguity.

Low/medium confidence relationship links must be routed to human review before acceptance.
