# Retrieval and MCP evidence

**Live LLM assistant deferred at the user's request.** No claim of live RAG answers, model tool selection, agent quality, cost or generated-answer reliability is supported yet.

Implemented: four read-only tools over frozen canonical results and a four-passage official-source lexical retrieval baseline. Actual MCP v2 stdio client/server handshake and calls are recorded in `evidence/ai/mcp-smoke.json`. Input limits, fixed tool names, a six-call budget and a 60-second deadline are enforced in client code. Server code exposes no general SQL, file or URL operation; annotations supplement that implementation.

Development tests cover numeric contracts, invalid arguments, outside-period requests, path/SQL-looking identifiers, withdrawn document exclusion and source-text trust labels. There is no model interpreting source text yet, so the prompt-injection test demonstrates data separation only, not model robustness.

A frozen 30-case tool suite ran over real MCP transport. **29/30 passed after correcting a scorer field-name error.** Original score 17/30 and raw responses are preserved. Twelve errors were successfully rejected by the server but initially mis-scored because MCP v2 serializes `is_error`, not `isError`. T29 is an observed retrieval failure: a mixed adversarial query failed to return the expected coverage passage. The retriever was not tuned after this result. No claim of broad reliability follows from this small suite.

Corpus dates mark when pages were checked; absent publication dates remain null rather than invented. Summaries are labelled paraphrases. Policy transition is current as checked 5 October; the old 2022 policy is not presented as a current requirement. Source passages cannot authorize tool access.

Pending live phase: model configuration, six-call/60-second orchestration across generation plus tools, citation-grounded answer checks, separate fresh 30+ held-out cases for ambiguity, conflicting/stale passages, injection, unsupported questions and tool selection. Embeddings are optional and would require relevance judgements and an honest comparison to this baseline. Avoid calling this completed LLM/RAG/agent experience on the résumé.

Following review, `scorer-amendment.json` binds the historical score files, canonical results, dependency lock and corrected scorer. Evaluation now verifies the original runtime/corpus/case freeze and that amendment before invoking tools, and writes only uniquely named files under `evidence/ai/regressions/`. A real MCP regression replay on 5 October again passed 29/30. It is a replay of seen cases, not an independent reliability estimate. Both historical score artifacts are unchanged.
