# Fact-Check Protocol for High Fact-Density Tasks (v2.2 + v2.4)

> Triggers when task has "hallucination tolerance = extremely low + citation requirement = academic-grade" (policy verification / BOM selection / Chinese primary source research / regulation clause verification / model license verification). Reports delivered directly from Recon **must undergo independent fact-checking** — the orchestrator and recon workers cannot self-score. "Independent" means *not the party that produced the claim*; it does not mean *a different vendor*. See the baseline/enhancement split immediately below: the required path runs on one model and its own tools.

## Layer -1 — Deterministic quote gate (run first, costs nothing)

Before any reviewer — human, model, or paid platform — run the quote checker that ships inside this skill. The orchestrator writes `<run_dir>/quotes.tsv` first (externalized input, same principle as `audit-input.tsv` below), then:

```bash
python3 "<skill_dir>/scripts/verify-quotes.py" \
  --run-dir "<run_dir>" --expected "<run_dir>/claims-expected.tsv"
```

Cheap deterministic matching first, expensive judgment only on what it cannot settle. Each `quote` claim is compared against its snapshot under `<run_dir>/snapshots/` — **the source text, never a worker artifact**: checking a quote against the artifact that produced it is the audited party supplying its own answer key, the same hole `validate-audit.py` exists to close (snapshot paths pointing into `artifacts/` are refused outright). Malformed rows are input errors, not skipped rows. `--expected` is the independent claim roster, written before the gate runs: strict parsing protects rows, not coverage, so without it a quotes.tsv cut to one valid row would report one passing claim and exit 0.

Boundary, stated no stronger: **given a snapshot accepted as authoritative**, the quote is a substring of it. It does not show the snapshot came from that URL, that quote and snapshot were not fabricated together, or that the source supports the claim — a passing quote still owes Mini Assurance its semantic audit. `unverifiable_capture` rows were verified by nothing and need manual review. URL reachability is separate and is not evidence.

## Layer 0 — Primary Source Locator Direct Reading (Principle 7 invariant)

For high-risk claims in the ledger **that have locators, read the primary source text directly to arbitrate** — this resolves most factual issues and **doesn't require paid DR / heterogeneous models**. Escalate to Layer 1/2 below only when:
1. Locator is missing or primary source is unreachable (walled-garden / academic full text)
2. Expansion set blind spot scanning is needed
3. Topic involves AI same-faction content requiring cross-faction false-humility dimension judgment

**Heterogeneous reviewers supplement blind spots; they don't replace missing primary source grounding.**

## Baseline vs. Enhancement — read this before the layers

**This protocol assumes one model and the tools it ships with.** That is the only configuration every install is guaranteed: an agent necessarily has one model, it does not necessarily have a second one, and it may have no subscription to any external Deep Research platform.

So the layers split into two groups, and **the mandatory path uses only the first**:

| | Layers | Needs |
|---|---|---|
| **Baseline — always runnable, always required when this protocol triggers** | **Layer -1** (deterministic quote gate), **Layer 0** (primary source locator direct reading), **Layer 2** (independent worker primary-source check), **Mini Assurance** | host model + web tools + a worker primitive |
| **Enhancement — run when available, never a blocker** | **Layer 1** (external Deep Research fact-check), **cross-faction reviewer** | a paid DR subscription / a second vendor family |

A run with no enhancement layers available is **fully conformant**. What it must not do is claim a check it did not perform: follow the same discipline Mini Assurance already uses for a missing worker slot — do the baseline layers, label the gap, and never report it as something stronger. Concretely, `fact_check_depth: baseline-only` in the audit, naming which enhancement layers were unavailable.

> Getting this wrong in the other direction is worse than skipping a layer. A step marked **mandatory that some hosts cannot perform** teaches the reader that "mandatory" is negotiable, and that lesson spreads to the steps that really are non-negotiable — the quote gate, the ledger status caps, the audit roster.

## v2.4 Pre-Check Discipline

1. **When an external DR platform is available, prefer its Deep Research mode over its quick-search mode** — fact-checking is a rigorous anchor-level task; **rigor > quota savings**. This ranks two modes of a platform you already have; it does not require acquiring one
2. **Cross-faction discipline** (triggers only for same-faction content) — When evaluating an AI vendor's products, benchmarks involving its own models, or its industry narratives, the final **false humility dimension judgment** should come from a reviewer in **another vendor family**; same-family workers are inherently blind to "appears self-deprecating but actually preserves faction advantage" high-dimensional PR-style bias, so a same-family reviewer cannot settle it. **When no second vendor family is reachable, this judgment is not available** — say so. Record `cross_faction: unavailable` and state that the false-humility dimension is unassessed; do not let a same-family reviewer stand in for it silently, and do not treat its verdict as a cross-faction result. An unassessed dimension that is labelled is recoverable; one that is quietly assessed by the wrong reviewer is not
3. **Cross-validation pairing — enhancement tier, only meaningful if you already hold these subscriptions**: Perplexity DR (Layer 1) + ChatGPT DR (cross-faction calibration) + Gemini DR (backup "expansion set blind spot scanning" — known "yi/billion" unit trap + excessive aggregate site acceptance)
4. **Data source 4-tier priority**: benchmark owner / regulation text / company official site (highest) > independent test > vendor self-report > aggregate site / mirror (lowest); large-gap numbers (≥10pp) must have owner direct citation; cross-tier discrepancies are not "conflicts" — both must be annotated

## Fact-Check Flow

### Layer 1 — External Deep Research fact-check (**enhancement**; skip when unavailable, label the skip)

- Only reachable with a subscription to an external DR platform. **Not required for conformance** — a run without one proceeds to Layer 2 and records `fact_check_depth: baseline-only`
- When available, prefer a platform whose strength is sentence-level citation and citation transparency; the point is a checker that does not rely on training data and is forced to pull authoritative sources
- Output: verdict table (✅/⚠️/❌/🟡) + inline citations
- What is lost by skipping it, stated plainly so the trade-off is visible: a second retrieval stack over the whole claim set. Layer 2 is narrower by design — it checks 1-2 blind spots, not everything

### Layer 2 — Independent worker primary-source check (**baseline**; the mandatory backstop, ~3 min, critical material only)

- Dispatch an independent worker through the current host to read primary sources directly (regulation text, vendor official pages, preprint servers)
- Trigger conditions (any one): ① a conclusion resting on a single source with no multi-source convergence ② policy-sensitive topic ③ critical material (core items affecting a business decision)
- **Don't re-run everything**, only check the 1-2 blind spots the earlier layers did not settle
- **When Layer 1 was skipped, this layer's selection input changes**: with no external verdict table to point at the weak spots, choose targets from the ledger itself — every `central` claim that is `weak`, `unresolved`, or resting on a single non-owner source. Say how many were selected and how many were checked

### Conflict Arbitration Order

1. If Layer 1 conflicts with the original report → trust Layer 1 (unless there's strong reason to doubt)
2. If Layer 1 conflicts with Layer 2 → must fall through to primary source direct reading (don't rely on LLM majority vote)
3. If **multiple LLM fact-checkers conflict with each other** → likewise fall through to primary source arbitration

### Empirical Cases

- **EU AI Act verification**: Perplexity Layer 1 was multi-source convergent and high-confidence on most items; a few blind spots were caught by Layer 2 primary source reading → two independent fact-checkers agreed on critical material, correcting several over-scored items in the original report.
- **License verification conflict**: The same EU AI Act report was fact-checked by both Gemini + Perplexity, which directly conflicted on DeepSeek-V3 license — Gemini said "all MIT" (wrong), Perplexity said "custom license" (correct). One `curl https://huggingface.co/deepseek-ai/DeepSeek-V3/raw/main/LICENSE-MODEL` resolved it. An LLM's self-assessed "95%+ accuracy" is a typical training-data recall over-confidence trap.
- **Self-bias audit**: A self-bias audit framework self-assessed as "passed" was **unanimously overturned** by cross-faction Deep Research — false-humility bias invisible to self-assessment is a natural blind spot for same-source reviewers. ~65% of worker citation sources came from aggregate sites; benchmark owner direct citations were < 30%.

---

## v3 Mini Assurance — Reviewer Reads Artifact Directly

> Generalization of v2.2 fact-check protocol — v2.2 only triggered for "high fact-density tasks"; v3 extends to all Recon direct delivery reports.
>
> **Core defense**: plausible unsupported success — the orchestrator reads worker summaries instead of raw artifacts, allowing worker micro-hallucinations to propagate to the final report.

**Trigger**: enabled by default for the Recon direct delivery branch (Step 3 selects "deliver directly"); user can skip with `--skip-mini-assurance`; high fact-density tasks continue using v2.2 fact-check (v3 is its generalization, no double-run).

**v2.5 lighter duty**: With Step 2.5's Claim Ledger, Mini Assurance no longer "re-extracts facts" but **audits whether the ledger supports the final report's topic sentences** — can each conclusion sentence trace back to a `confirmed` (not `weak`/`unresolved`) claim in the ledger. **Adjudication mode**: split by sentence type — **fact sentences** map to the Claim Ledger as above; **conclusion / argument sentences** map to the Hypothesis Matrix instead (see the Adjudication task bullet below), not required to trace to a "confirmed fact."

### Flow

After the report draft is generated but before output to user, dispatch a **fresh reviewer worker** through the current host (independent context, does not read the draft's "summary / conclusions" sections).

**No-slot fallback (must be explicit in the audit):** If the host has no **fresh worker slot**, first reuse an **idle independent worker** that did not participate in this run and give it only the ledger, raw artifact paths, and key-claim list. If no independent worker is available, the orchestrator performs the same artifact-only checks as a **non-independent fallback**, labels `audit_independence: degraded`, and never reports this as an independent review. Do not silently omit Mini Assurance.

Reviewer input:
- **Claim Ledger** (`<run_dir>/ledger.md`) + **evidence artifacts only** — the Round 1 (2B) and Round 2 worker outputs under `<run_dir>/artifacts/`, persisted by the orchestrator in Step 0 — + draft's "key claim list"
  - **`artifacts/00-discovery.md` is excluded.** Step 2A reads nothing deeply and produces no ClaimCards; the file holds leads — the named-entity list, plus whatever an optional external pass contributed — and index listings whose whole point is that they were *not* verified. Handing it to the reviewer under an `artifacts/*.md` wildcard would let a lead be labelled `supported` — which quietly reverses 2A's "lead, not evidence" rule. It may be used for a coverage question ("was this angle searched?"), never to support a claim.
- **(Adjudication only) extracted `warrant_records[]`**: `conclusion_id / hypothesis_id / evidence_ids / warrant / qualifier / key_defeater / contrary_claim_ids` — so the reviewer can audit each load-bearing conclusion without reading the draft's conclusions section (the conclusion sentences arrive here as extracted entries, not by reading the draft)
- **Task**: for each report topic sentence, assign one of 3 labels:
  - ✅ `supported`: artifact contains original text support (must attach artifact path + key sentence)
  - ⚠️ `unverifiable`: not found in artifact (goes to "needs manual verification" list)
  - ❌ `conflict`: artifacts contradict each other (explain conflict point)
- **★ Adjudication conclusion / argument sentences**: audit fact sentences against the ledger as above; **reasoning / conclusion sentences are checked against the Hypothesis Matrix via the extracted `warrant_records[]`** (below) — verify the evidence IDs exist with acceptable ledger status, the warrant sufficiently supports the conclusion, the qualifier matches evidence strength, and **known contrary claims / defeaters are complete and materially addressed** (not "zero contradicting claims"). Don't mislabel warrant / rebuttal reasoning sentences as `unverifiable` noise.
- **Mandatory scope**: all numbers / strong recommendations / causal claims / person/company/time factual assertions
- **Spot check**: 20% random sample of soft judgments
- **Prohibited**: reading draft's "summary / conclusions" sections; changing writing style; filling in claims; outputting rewrite suggestions

**Output**: append a `## Mini Assurance Audit` section at the end of the final report (3-label stats + unverifiable/conflict list + artifact reference paths), and persist the same section to `<run_dir>/audit.md`.

---

### Completeness is a machine-checked contract, not an instruction

*(Added 2026-08-04. Until then this file said only "for each report topic sentence" — an intent with nothing enforcing it, and the audit silently degraded into a rubber stamp.)*

**One input sentence ⇒ exactly one verdict row. Sentence IDs must correspond one-to-one.**

Because the party being checked cannot also supply the answer key, the orchestrator persists the authoritative input set **before dispatching the reviewer**:

```
<run_dir>/audit-input.tsv     # one line per topic sentence:  S01<TAB>fact<TAB><sentence>
```

The reviewer's `audit.md` must contain a line of its own reading `input_sentence_count: N`
(ASCII key — a Chinese/prose phrasing like "输入 N 句" gets falsely matched by any "N sentences" in the body),
followed by one row per sentence: `S01 | supported|unverifiable|conflict | <artifact path + key sentence>`.

Validate with the checker that ships **inside this skill** — byte-identical in every generated target, so the rule cannot drift between hosts:

```bash
python3 "<skill_dir>/scripts/validate-audit.py" \
  --expected "<run_dir>/audit-input.tsv" --audit "<run_dir>/audit.md"
```

`<skill_dir>` is wherever this skill was unpacked. The checker is stdlib-only Python 3 — no install step, no network.

> **If you cannot run it** — no Python 3, a sandbox that blocks execution, a host without a shell — the contract above still binds, but *nothing is enforcing it*. Then **say exactly that in the audit** rather than reporting a gate as passed. A gate nobody runs is the failure mode this whole section exists to document.

It rejects all four evasions: **range collapse** (`| S01–S19 | supported ×19 |`), **omitted sentences**, **a repeated ID padding the row count**, and **IDs absent from the authoritative list**. Failure ⇒ re-dispatch the reviewer once; failing again ⇒ mark the whole run `partial`, never deliverable.

> **Why the answer key is externalized** — 2026-08-03 a reviewer collapsed 27 sentences into 2 summary rows and the gate printed "✅ passed", exit 0. The same question audited sentence-by-sentence had caught 1 `unverifiable`; the collapsed version reported 0. The first fix compared row count against a number **declared inside `audit.md` itself**, so a reviewer that collapsed to 2 rows and declared "2 sentences" still passed. Any check whose baseline comes from the audited party is decorative.

> **Scope boundary — do not oversell this.** It validates *structure* only. A reviewer can still label every sentence `supported` and pass. This gate stops collapse, omission and fabrication; it does not stop *wrong* verdicts.

**Cost**: +5-10 min per research run, +10-15% tokens. **Expected effect** (internal estimate, not a benchmarked result): fewer unsupported claims reach the final report.

**Upgrade path** (evaluate reviewer hit rate after accumulating cases):
- < 5% hit rate → tighten rubric
- 10-30% hit rate → maintain current approach
- > 50% hit rate → upstream Recon quality issue, strengthen worker instructions
