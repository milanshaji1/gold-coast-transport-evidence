# MCP tools and retrieval

The project includes a small MCP (Model Context Protocol) server so an AI assistant can query the results without touching the raw data or running its own SQL.

## What's there

- **Four read-only tools** in `src/transport/server.py`: `aggregate_stats` (crash counts for a period and severity), `inspect_area` (one shortlisted square), `quality_provenance` (data quality and limits) and `search_documents` (search a small set of official source passages).
- **Lexical retrieval** (TF-IDF) over four short passages from the Queensland crash dataset and TMR road-safety pages. Retrieved text is labelled as untrusted source text, and withdrawn documents are excluded.
- **Guard rails in the client** (`src/transport/client.py`): a fixed list of allowed tools, a limit on argument size, at most six calls per request and a 60-second deadline. The server has no general SQL, file or URL access.
- A real stdio client/server exchange is recorded in `evidence/ai/mcp-smoke.json`. Run one yourself with `PYTHONPATH=src .venv/bin/python -m transport.client`.

## Evaluation

A fixed set of 30 cases (`evidence/ai/final-tool-cases.json`) runs over the real MCP transport. It covers correct counts, invalid periods and severities, SQL- and path-like inputs, out-of-range limits, unrelated questions and retrieval.

**Result: 29/30.** The first scoring run reported 17/30 because the scorer looked for the field `isError`, while MCP v2 returns `is_error`. Twelve calls had been correctly rejected by the server but were scored as failures. Both the original and corrected result files are kept, and `evidence/ai/scorer-amendment.json` records the correction.

The one real failure is T29: a query mixing injection-style text with "crash coverage" didn't return the expected passage. The retriever wasn't tuned afterwards to make it pass.

Rerunning these 30 cases is a regression check, not a fresh reliability estimate, because the cases are already known. Reruns are saved under `evidence/ai/regressions/`; the 5 October rerun also passed 29/30.

## Not in this version

There's no live language model in this release, so there are no claims about generated answers, tool choice by a model, or answer quality. A next step would add a model, test it on a fresh set of held-out questions (ambiguous, conflicting, unsupported and injection cases), and compare any embedding-based retrieval against this TF-IDF baseline.
