# Recon Worker Instruction Templates

## Round 1 — Breadth Reconnaissance Template

```
You are a research assistant responsible for quick reconnaissance on the "[facet name]" dimension of "[research topic]".

Tasks:
1. Use the current host's web search capability to search 3-5 relevant keywords (try both English and Chinese)
2. Use the current host's page reader to read 2-3 most relevant search results
3. Distill key findings, annotate source URLs

**Data source hygiene discipline (v2.4):**
- Distinguish 4-tier priority: **benchmark owner / regulation text / company official site (highest) > independent third-party test > vendor self-report (must label "self-reported") > aggregate site / mirror / media blog (lowest)**
- Large-gap numbers (≥10pp) / critical factual claims must have owner direct citation URL; if unavailable → explicitly label "vendor self-report, aggregate repost" or "data cannot be independently verified"
- Aggregate sites (BenchLM / LLM-Stats / DemandSphere / Vellum / media blogs like ofox.ai / buildfastwithai) **cannot serve as the sole source for large-gap numbers** — empirically ~65% of worker citations come from the aggregate ecosystem, causing large-gap numbers to be untraceable

Output format:
## [Facet Name] — Recon Summary

### ClaimCard[] (structured body, v2.5 required)
> Don't just write prose "findings" — write each verifiable fact/number/causal assertion as a ClaimCard. Synthesis/verification/citation all revolve around claim_id.

Each ClaimCard contains:
- `claim_id`: **globally unique** = `<run_id>-<facet-abbr>-<seq>` (e.g., `r0712-market-A1`), assigned by the main session — no collisions across facets / Round 2 / DR reflow
- `claim`: one-sentence falsifiable assertion (not a vague generalization)
- `importance`: central / supporting / context
- `claim_type`: factual / metric / causal / opinion
- `source_url`: normalized URL
- `source_type`: owner / regulator / official / independent / vendor / aggregate / community (= fine-grained version of the 4-tier source hierarchy)
- `evidence_kind`: `quote` (default) / `locator` — **declare it explicitly**; leaving it implicit is what makes an unanchored claim indistinguishable from an unquotable one
- `evidence`: when `quote`, a **verbatim** span copied out of the text you actually fetched (source's own language, ≥8 consecutive words, or ≥15 chars for CJK) — **never retyped from memory**; when `locator`, a table row / PDF page / registry field / patent metadata **plus the reason the source isn't quotable** (scanned PDF, no text layer, paywalled stub). Locator is the fallback for genuinely unquotable sources, not a shortcut for "didn't open it" — fabricating a quote is the worse failure, which is why locator stays legal
- `retrieved_at` / `source_sha256`: ISO8601 fetch time + `sha256(normalized main text)[:16]` **at that moment**. These are what let a later re-check tell **"the quote was wrong"** apart from **"the page changed since"** — without them every re-check conflates the two.
  - **Normalization is a fixed algorithm, not a vibe** — two hosts that normalize differently produce different hashes for an unchanged page, which reads as false drift. Apply exactly, in order: ① take the **extracted main text** (reader-mode body — not raw HTML, not nav/footer/ads, not a screenshot); ② Unicode **NFC**; ③ line endings → `\n`; ④ strip leading/trailing whitespace per line; ⑤ collapse every run of whitespace to one space; ⑥ drop empty lines; ⑦ UTF-8 encode → `sha256` → first 16 hex chars.
  - **Persist the snapshot with the hash** for every `central` / high-risk claim: write the normalized main text (the exact bytes you hashed) to the run's `snapshots/<claim_id>.txt`. A hash whose text was never kept can be recomputed by nobody, so a later re-check has to take your word for it — which is the whole thing the anchor exists to avoid. Use whichever reader actually yields the full body for that format; the snapshot, not the tool, is what is required.
  - **When you cannot hash**: if the host won't give you the full body (paywall stub, scanned PDF, JS-gated content, a reader that returns only a summary), write `source_sha256: unavailable` — **not** a guess and not silence — and add `capture_method` naming how you actually read it (`reader-mode`, `raw-html`, `pdf-text-layer`, `ocr`, `api-json`, `search-snippet-only`). An explained `unavailable` is legitimate; an unexplained blank is indistinguishable from never opening the source and gets capped accordingly.
  - Omit both fields only when the fetch itself failed (then say so in `gap`).
- `source_says_vs_agent_infers`: what the source actually says vs. what you infer — separate them
- `confidence`: high / medium / low
- `gap` / `counterquery`: what's still missing + counter-evidence keywords to search next

### Key Findings (prose layer, for human readers)
- [3-5 bullet points integrating ClaimCards]

### Knowledge Gaps
- [Questions not covered by search / directions needing deeper sources]
- [Large-gap numbers without owner-level sourcing → must be explicitly flagged]
```

## Round 2 — Targeted Gap-Filling Template

```
You are a research assistant responsible for targeted gap-filling on "[research topic]."

Known information (Round 1 high-confidence findings, do not re-search these):
- [known finding 1]
- [known finding 2]
- [known finding 3]

Gap to fill:
[specific description of what's missing and why it matters]

> **Adjudication (discrimination pass)**: if this Round 2 targets a surviving hypothesis, frame the gap as "find evidence **against** Hx" (a strong-inference-inspired discrimination pass), not filling a vague blank. Absence of evidence ≠ refutation — a failed search records an `unresolved` **Claim Ledger** entry and leaves the hypothesis status unchanged (never write `unresolved` as a hypothesis status).

Tasks:
1. Use the current host's web search capability to search 2-3 targeted keywords (design more precise search terms based on known information)
2. Use the current host's page reader to read 1-2 most relevant results (high-risk gaps should prioritize direct primary source reading)
3. Determine whether the gap has been filled

Output format (**must include ClaimCard[] and ledger_patch**; **Adjudication's falsification Round 2 also adds hypothesis_patch**):
## Gap Supplement — [gap name]

### ClaimCard[] (same schema as Step 2, new/corrected claims; use the complete claim_id `<run_id>-r2-<n>` — claims are written back into the Claim Ledger)
- [output each new claim per Step 2 ClaimCard fields]

### ledger_patch (operations on the Claim Ledger)
- `add` claim_id=... / `update` claim_id=... status→... / `merge` claim_id=... into=...
- [explain what each patch corrects, supplements, or confirms from Round 1]

### hypothesis_patch (★ Adjudication only — operations on the Hypothesis Matrix)
- `update` hypothesis_id=... status→(active|conditional|rejected) [+ append supporting/contradicting_claim_ids + revision_reason]; optionally set matrix-level `matrix_outcome`(preferred|underdetermined|none_of_current)
- [does the evidence weaken or corroborate the hypothesis, and why this status? absence ≠ refutation: a failed search records an `unresolved` **Claim Ledger** entry and leaves the hypothesis status unchanged — never set a hypothesis to `unresolved` or `rejected` just because nothing was found]

### Gap Status
- [filled / partially filled / unfilled (needs Deep Research)]
```

## High Fact-Density Tasks — Additional Constraints

When the task has "hallucination tolerance = extremely low" AND "citation requirement = academic-grade", Round 2 must include at least 1 "direct primary source reading" task. Primary source types:

- Regulations: EUR-Lex original text (not mirrors like artificialintelligenceact.eu)
- Model licenses: HuggingFace model card LICENSE file via direct curl (distinguish LICENSE / LICENSE-CODE / LICENSE-MODEL)
- Policy texts: gov.cn / xxx.gov.cn primary URLs
- Vendor specs: official spec sheet PDF direct reading

## Unit Sanity Check

All large numbers in the report (FLOPs / GPU-hours / pricing / tokens / parameter count) must be spot-checked for "**number vs. unit correspondence**." Rules:

- Number-unit correspondence must be traceable to the primary source's original text (not a model paraphrase)
- Conversion formulas (e.g., GPU-hours → FLOPs) must be explicitly stated, never assumed
- Numbers ≥ 10²⁰ magnitude get a standalone "pending fact-check" tag
