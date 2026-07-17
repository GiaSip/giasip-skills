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
confidence: high             # high | mid | low
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
- **Mini Assurance** — before delivery, a *fresh* reviewer with its own context re-reads the **raw evidence artifacts**, not the summary, and labels each conclusion `supported` / `unverifiable` / `conflict`. Reading the raw evidence is what defeats evaluator leakage.

## Eating our own dog food

This page makes one claim worth auditing by its own method:

> "The Claim Ledger and fresh-reviewer gates raise accuracy from ~70–80% to ~85–90%."

Run it through the gate and it looks like this:

```yaml
claim_id: method-doc-B1
claim: "The gates raise accuracy from ~70-80% to ~85-90%."
importance: central
claim_type: metric
source_type: vendor          # this is our own self-report
evidence: "a small number of internal cases; 'accuracy' not formally defined, N small, no public rubric"
source_says_vs_agent_infers:
  source_says: "internal cases moved in this range"
  agent_infers: "the gates are what caused the improvement"
confidence: low
status: weak                 # vendor-only, no independent locator -> quarantined
gap: "no benchmark, no defined metric, no external replication"
counterquery: "does claim-level verification measurably reduce hallucination in research agents"
```

By the method's own rules the number is `weak` — a vendor self-report with no independent locator — so it belongs in "to be verified," not in a conclusion. We keep it here, labeled honestly, because a method about calibrated trust should be willing to apply that calibration to itself.

## Using it

The method ships as the `giasip-research` skill for Claude Code and Codex. See the [repository README](../README.md) to install and run it, and [`examples/`](../examples/) for a worked run showing a bounced claim.
