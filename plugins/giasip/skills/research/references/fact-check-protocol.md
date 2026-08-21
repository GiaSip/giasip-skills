# Fact-Check Protocol for High Fact-Density Tasks (v2.2 + v2.4)

> Triggers when task has "hallucination tolerance = extremely low + citation requirement = academic-grade" (policy verification / BOM selection / Chinese primary source research / regulation clause verification / model license verification). Reports delivered directly from Recon **must undergo independent fact-checking** — the orchestrator and recon workers cannot self-score.

## Layer -1 — Deterministic quote pre-check (run first, costs nothing)

Before any reviewer — human, model, or paid platform — run the quote checker that ships inside this skill against the run's **source snapshots**:

```bash
python3 "<skill_dir>/scripts/verify-quotes.py" --run-dir "<run_dir>"
```

Cheap deterministic matching first, expensive judgment only on what it cannot settle. It compares each `quote` claim against `<run_dir>/snapshots/<claim_id>.txt` — **the source text, never a worker artifact**: checking a quote against the artifact that produced it is the audited party supplying its own answer key, the same hole `validate-audit.py` exists to close. Only failures go to a reviewer. It validates that the quote **appears in the source**, not that the source supports the claim; URL reachability is reported separately and is not evidence.

## Layer 0 — Primary Source Locator Direct Reading (Principle 7 invariant)

For high-risk claims in the ledger **that have locators, read the primary source text directly to arbitrate** — this resolves most factual issues and **doesn't require paid DR / heterogeneous models**. Escalate to Layer 1/2 below only when:
1. Locator is missing or primary source is unreachable (walled-garden / academic full text)
2. Expansion set blind spot scanning is needed
3. Topic involves AI same-faction content requiring cross-faction false-humility dimension judgment

**Heterogeneous reviewers supplement blind spots; they don't replace missing primary source grounding.**

## v2.4 Pre-Check Discipline

1. **Default mode = Deep Research** (reverting "Pro Search normal mode" default) — fact-checking is a rigorous anchor-level task; **rigor > quota savings**; Deep Research quota exists for exactly this type of task; regular Pro Search is only for ad-hoc lightweight verification
2. **Cross-faction mandatory discipline** (triggers only for same-faction content) — When evaluating an AI vendor's products, benchmarks involving its own models, or its industry narratives, **at least one reviewer from another vendor family must be used** for the final **false humility dimension judgment**; same-family workers cannot serve as the final arbiter — they are inherently blind to "appears self-deprecating but actually preserves faction advantage" high-dimensional PR-style bias
3. **Cross-validation recommended pairing (v2.4)**: Perplexity DR (Layer 1 primary) + ChatGPT DR (cross-faction calibration, replacing Gemini) + Gemini DR (backup "expansion set blind spot scanning" — known "yi/billion" unit trap + excessive aggregate site acceptance)
4. **Data source 4-tier priority**: benchmark owner / regulation text / company official site (highest) > independent test > vendor self-report > aggregate site / mirror (lowest); large-gap numbers (≥10pp) must have owner direct citation; cross-tier discrepancies are not "conflicts" — both must be annotated

## Fact-Check Two-Layer Flow

### Layer 1 — Perplexity Deep Research Primary Fact-Check (~5 min; downgrade to Pro Search only for ad-hoc lightweight verification)

- Perplexity Deep Research recommended as primary — sentence-level citation + industry-leading citation transparency is its strength
- Does not rely on training data, forces web search to pull authoritative sources
- Output: verdict table (✅/⚠️/❌/🟡) + inline citations

### Layer 2 — Independent Worker Primary-Source Check for Perplexity Blind Spots (~3 min, critical material only)

- Dispatch an independent worker through the current host to read EUR-Lex / vendor official / arxiv primary sources
- Trigger conditions (any one): ① Perplexity single-source conclusion (no multi-source convergence) ② policy-sensitive topic ③ critical material (core scoring items affecting business decisions)
- **Don't re-run everything**, only check 1-2 blind spots Perplexity didn't fully verify

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
- **Claim Ledger** (`<run_dir>/ledger.md`) + Round 1/Round 2 worker artifacts (`<run_dir>/artifacts/*.md`, persisted by the orchestrator in Step 0) + draft's "key claim list"
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
