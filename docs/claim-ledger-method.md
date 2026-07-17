# The Claim Ledger Method

*How `giasip-research` keeps a research agent from reporting things it can't back up.*

## The one-paragraph version

Most research agents optimize for **retrieval breadth** — search more, read more, summarize. But breadth was never the bottleneck; **trust calibration** is. The Claim Ledger Method treats every checkable fact an agent finds as a discrete, auditable **claim** — each carrying an explicit confidence rating and a tag for *what kind of source* backs it — and runs those claims through gates that keep unsupported ones out of the conclusions. The report you read is still ordinary prose; the ledger is the audit trail behind it.

## The problem: plausible, unsupported prose

A language model writes confident prose whether or not the underlying facts are grounded. Three failure modes recur in research tasks:

1. **Aggregator laundering** — a number originates on one blog, gets copied across five aggregator sites, and now *looks* corroborated. Five copies of one source are not five sources.
2. **Source-said vs. agent-inferred drift** — the source says "applies from 2 August 2025"; the agent writes "you must be fully compliant by then," quietly adding a claim the source never made.
3. **Evaluator leakage** — a supervising agent reviews a worker's *summary* instead of the raw evidence, so a small hallucination in the summary is never caught.

The method is built to make each of these structurally hard.

## The atomic unit: a ClaimCard

Instead of a sentence buried in a paragraph, each checkable fact is recorded as a card:

```yaml
claim_id: r0716-market-A1
claim: "The EU AI Act's GPAI obligations apply from 2 August 2025."
importance: central          # central | supporting | context
claim_type: factual          # factual | metric | causal | opinion
source_url: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
source_type: regulator       # owner | regulator | official | independent | vendor | aggregate | community
evidence: "Art. 113(b) — locator: OJ text, applicability section"
source_says_vs_agent_infers:
  source_says: "applies from 2 August 2025"
  agent_infers: "GPAI providers must comply by that date"
confidence: high             # high | medium | low
gap: "no consolidated English text of the delegated timeline yet"
counterquery: "EU AI Act GPAI obligations start date delayed 2025"
```

Two fields carry most of the weight:

- **`source_type`** records the *family* of the source, because not all corroboration is equal (see the ladder below).
- **`source_says_vs_agent_infers`** forces the agent to separate the quote from its own inference — the single cheapest defense against drift.

## The source-family ladder

Corroboration is weighted by where it comes from, highest to lowest:

`owner / regulator / official`  >  `independent`  >  `vendor` (self-reported)  >  `aggregate / community`

A high-stakes number — a ≥10-percentage-point gap, a price, a license term — needs a citation from the top of the ladder. Five aggregator copies do not clear the bar.

## The gate: what stops an unsupported claim

All claims are merged into one **Claim Ledger** and passed through a gate before anything reaches your conclusions:

- **Deduplicate** by URL *and* by claim-level meaning — five reposts of one figure collapse to a single entry (`merged_from: 5`).
- **Flag high-risk** — a claim is high-risk if it's a ≥10pp number, a license term, a policy/legal/financial fact, or an assertion about the model's own camp.
- **Bounce locator-less central claims** — a `central` claim with no primary-source locator is sent back for another, more targeted search round. It does not get to sit in a conclusion on faith.
- **Quarantine weak claims** — a central claim backed only by vendors or aggregators is marked `weak` and moved to a "to be verified" list. It can be *mentioned*, never *concluded*.
- **Don't confuse uncertain with refuted** — a claim only becomes `refuted` when there is explicit conflicting evidence; otherwise it stays `unresolved`.

## The order most agents get backwards

When claims conflict, the method resolves them in this order — deliberately the opposite of the common assumption:

> **primary-source grounding  >  source-family convergence  >  cross-model cross-check**

Multi-model cross-checking is widely treated as the gold standard. Here it ranks **last**. One model that actually read the primary source beats three models cross-checking each other from memory. Heterogeneous reviewers are for catching blind spots — they are not a substitute for a primary source nobody read.

Two special cases sit on top of this order:

- **Cross-faction fact-check** — when the topic touches the reviewing model's own camp (e.g. judging its own vendor's product), the final verdict must include a model from a different camp; a same-family reviewer has a structural blind spot.
- **Mini Assurance** — before delivery, a *fresh* reviewer with its own context re-reads the **raw evidence artifacts**, not the summary, and labels each conclusion `supported` / `unverifiable` / `conflict`. Reading the raw evidence is what defeats evaluator leakage. (This runs by default on direct-delivery research; it can be skipped, and if no independent reviewer is free it falls back to a clearly-labeled `degraded` audit rather than pretending to be independent.)

## Eating our own dog food

This page makes one claim worth auditing by its own method:

> "The Claim Ledger and fresh-reviewer gates raise accuracy from ~70–80% to ~85–90%."

Recorded as a ClaimCard it looks like this:

```yaml
claim_id: method-doc-B1
claim: "The gates raise accuracy from ~70-80% to ~85-90%."
importance: central
claim_type: metric
source_url: null             # no external source exists — which is the whole problem
source_type: vendor          # our own self-report
evidence: "documented only as an 'expected effect' — no benchmark, no defined metric, N unknown"
source_says_vs_agent_infers:
  source_says: "an expected effect, stated as a hypothesis"
  agent_infers: "the gates are what cause the improvement"
confidence: low
gap: "no benchmark, no defined metric, no external replication"
counterquery: "does claim-level verification measurably reduce hallucination in research agents"
```

In the Claim Ledger this lands as `status: weak` — a central, vendor-only claim with no independent locator, so it's quarantined to "to be verified," never stated as a conclusion. We keep it here, labeled honestly, because a method about calibrated trust should apply that calibration to itself.

## The ledger governs the whole supply chain

The gates above run on the cheap first pass, but the same ledger stays in charge through the expensive parts too:

- **Recon before paid escalation.** By default a short in-house recon runs first, and a paid Deep Research platform is engaged only for gaps native search can't reach — though the user can skip recon and go straight to Deep Research when that's the known need. Before spending, it reports the platform and estimated count/cost and waits for approval, unless the user has pre-authorized direct submission.
- **Confirmed-only seeding.** The Deep Research prompt is built from `confirmed` ledger claims only. `weak` and `unresolved` claims are withheld, so the paid run isn't anchored to something the ledger hasn't verified.
- **Reflow, not trust.** The returned Deep Research report is not pasted in. Its claims are extracted into ClaimCards, passed through the same gate, and reconciled against the recon ledger — a paid platform hallucinates too, and its conclusions do not automatically override a primary source the recon already grounded.
- **Persistence and resume.** Each run persists its manifest, raw artifacts, ledger, prompts, and audits. Because a Deep Research run can take an hour and the user may return in a new session, the manifest records the run state (`in_recon` / `awaiting_user_dr` / `delivered` / …) so work resumes without loss.

So a claim is the single accounting unit from the first cheap search to the last paid report. That end-to-end custody — not the number of search rounds — is what the word *orchestrator* is doing here.

## Lineage

The method doesn't claim every move is new. Two ideas are borrowed on purpose:

- **Claim-level quality control** — raising reliability from "summary-level" to "claim-level," and shifting that control left to the extraction stage — follows the claim-level QC approach in the deep-research skill of Claude Code Workflow.
- **Interactive Scaling** — the second, targeted search round that searches *again with the first round's knowledge* instead of re-broadcasting breadth — follows [MiroThinker](https://github.com/MiroMindAI/MiroThinker)'s Interactive Scaling.

The multi-round dispatch mechanics themselves are table stakes for any deep-research harness. What this method adds on top is the part that governs the whole supply chain: the source-family verification order (primary-source > cross-model), confirmed-only seeding of paid runs, re-gating of returned Deep Research through the same ledger, cross-session persistence, and the artifact-reading Mini Assurance audit.

## Using it

The method ships as the `giasip-research` skill for Claude Code and Codex. See the [repository README](../README.md) to install and run it, and [`examples/`](../examples/) for a worked run showing a bounced claim.
