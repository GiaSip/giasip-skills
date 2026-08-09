# Hypothesis Spine — the Argument-Validity Axis (third axis)

> GiaSip Research's third axis: converge scattered facts into **evidence-tested** claims. **Engaged for Adjudication mode only.**
> `SKILL.md`'s core path holds only the trigger points; schema / discipline / provenance live here.
> The three axes: coverage (Round 1 + Round 2) · factual certainty (Claim Ledger) · **argument validity (this axis)**.
> Provenance: Chamberlin's method of multiple working hypotheses (1897) / Platt's strong inference (1964) / Analysis of Competing Hypotheses (Heuer, CIA) / Toulmin's model of argument (1958). The axis checks **evidential and inferential support** (not formal logical validity — see §5).

## 1. Three research modes (fix at Step 1, write into manifest.md)

| Mode | Output goal | Hypothesis Spine |
|---|---|---|
| **Retrieval** | a single fact / price / definition / list | skip |
| **Mapping** (default) | survey / landscape / taxonomy / non-adjudicative comparison | coverage only; do not force hypotheses |
| **Adjudication** | why / causation / evaluation / recommendation / decision ("should we", "which is better") | **fully engaged** |

- **If the classification is unclear → default to Mapping**; escalate to Adjudication only when the requested sub-question **requires comparing plausible explanations or options and defending an inferential judgment** (even if the final outcome is `underdetermined`). This conservative default avoids unnecessary procedural overhead.
- **Route mixed tasks per sub-question**; do not assign one mode to the whole task ("look into industry X" that implies "should we enter" → handle the sub-questions separately).
- **Two-stage classification**: Step 1 gives a provisional mode + recheck after Round 1 returns — "do the Round 1 findings require **comparing plausible competing answers to the same question**? Yes (and at least two live candidates exist) → escalate to Adjudication even if Step 1 tagged Retrieval/Mapping". (Note: sources merely *disagreeing on a fact* is Claim Ledger conflict arbitration, not Adjudication.) This prevents an argumentative task being silently misjudged as retrieval and the spine quietly never firing.

## 2. Hypothesis Matrix (in the same `ledger.md`, a separate section, **NOT in the Claim Ledger**)

```
# per-hypothesis
hypothesis_id
candidate_answer            # one candidate answer to the user's core question
type(causal | decision | forecast)
supporting_claim_ids        # links to Claim Ledger claim_ids (many-to-many)
contradicting_claim_ids
discriminator_or_falsifier  # what evidence/observation would distinguish it (or, for causal, disprove it)
status(active | conditional | rejected)
revision_history            # frozen versions; record a reason for each change
residual_uncertainty

# matrix-level (the overall comparison, not one hypothesis)
matrix_outcome(preferred | underdetermined | none_of_current)
preferred_hypothesis_id     # set only when matrix_outcome = preferred
```

**Claim Ledger vs Hypothesis Matrix — the operational boundary**: an atomic, externally supportable claim (including "Study X reports Y", and causal or opinion claims a source actually states) enters the **Claim Ledger**; the orchestrator's own **synthesized** causal / evaluative / decision / forecast conclusion enters the **Hypothesis Matrix**.

**Why separate, not folded into the Claim Ledger**:
- The Claim Ledger answers "is this claim reliable"; the Hypothesis Matrix answers "how do these claims support/weaken candidate explanations" — the two have different `status` semantics (a confirmed claim ≠ a supported hypothesis; "not yet rejected" ≠ true).
- Mixing them would ① pollute the Claim Ledger's confirmed/weak/unresolved/refuted semantics; ② create a **circular self-justification hole**: a conclusion sentence "X is the best choice" maps to a hypothesis carrying a "surviving" status → Mini Assurance sees a supporting entry and passes it, but what should actually support it is the claims underneath the hypothesis = the audit passes without independent evidentiary support.
- Traceability is achieved with **link fields**, no shared table needed: Round 2 emits a `hypothesis_patch` (`update hypothesis_id=... status→...`), and the Claim-layer gate/audit logic is unchanged.

## 3. Forming hypotheses — discipline (in Step 2.5, after breadth + the Claim Ledger Gate)
- **Form them after breadth** (to prevent anchoring; "form later" only mitigates, doesn't eliminate, hence the discipline below).
- **2-3 competing candidate answers (default, not a hard rule), and must include one null / status-quo / "not worth doing" hypothesis** — to prevent nominal alternatives that share the same underlying assumption (when evaluating a market opportunity, don't make all three "enter now / enter in six months / enter differently").
- Give each hypothesis a **type-appropriate discriminator** (see §4) — a test that would distinguish it from the others or, where applicable, disconfirm it.
- **Originate at least one candidate by backward reasoning, not only forward projection** — fix a result worth existing and reverse-engineer the hypothesis that would produce it (Schulman's reverse method), so the set does not silently share the source framing's hidden assumption (this gives a *generative* technique for the null/different-assumption requirement above, which otherwise only warns against nominal alternatives). Optionally calibrate with *predict-before-you-look*: record your expected outcome per candidate before Round 2 returns, exposing where a prior is load-bearing. (Practitioner heuristic, not a formal method — from a research-practice thread by @itsreallyvivek on X; the disconfirming-evidence ethos it also preaches is already covered by §4 / Chamberlin-Platt, deliberately not re-grafted.)

## 4. Discrimination / convergence discipline (Round 2 + Step 3)
- The umbrella instruction is **"seek discriminating or disconfirming evidence"**, applied by hypothesis type:
  - **causal**: design Round 2 queries that could **disprove** the causal premise (a strong-inference-inspired discrimination pass); the worker prompt says outright "find evidence **against** Hx" (a fresh worker can reduce anchoring, but the prompt must still request symmetric treatment of supporting and contrary evidence).
  - **decision (`should`-type)**: separate the testable **factual premises** (searchable — adversarially test them and include a do-nothing option) from the **value weights / risk preferences / decision thresholds** that evidence cannot settle (state the latter explicitly; don't pretend "evidence" resolved them).
  - **forecast**: update probabilities + condition on scenarios, with disconfirming indicators; do not "disprove" the future.
- **Absence of evidence ≠ refutation**: only **explicit conflicting evidence** or a **failed predicted observation** rejects a hypothesis. A failed search creates an `unresolved` **Claim Ledger** entry (or a search note) and **leaves the hypothesis status unchanged** — "not found" is never written as a hypothesis status.
- **Allow 0 / 1 / many survivors**; **do NOT** treat "converging to a single hypothesis" as a success KPI — forcing a single survivor = rejecting an un-refuted hypothesis to fit a format = premature closure = confirmation bias (exactly what the spine is meant to prevent).
- A legitimate matrix outcome is **`underdetermined`**: multiple hypotheses coexisting + the conditions under which each holds + which evidence would decide between them.
- **Freeze versions**: once a hypothesis is recorded, any later change must record a `revision_reason` (prevents HARKing / moving the goalposts).
- **Round 2 cap stays at 1 round** (no stopping rule = infinite loop).

## 5. Warrant gate (Step 3, load-bearing conclusions only)
Minimal format: `claim / evidence IDs / warrant (reason) / qualifier / key defeater`
- The audit is **not** "are there zero contradicting claims" (a preferred hypothesis may legitimately have some, and requiring zero would reward omission). A fresh reviewer verifies that: the evidence IDs exist and have acceptable ledger status; the warrant is relevant and sufficiently supports the conclusion; the qualifier matches the evidence strength; and **known contrary claims and defeaters are complete and materially addressed — no unaddressed decisive contradiction after a documented countersearch**. This makes the third axis **actually audited**, rather than living only in the output format.
- Not every sentence needs it; self-evident light conclusions skip it.
- Note: Toulmin is an **argument-analysis framework, not a formal validity test**, so don't chase "all six parts" — use these 5 fields.

## 6. Quality-control invariant, split by sentence type (Step 3 / Mini Assurance)
- **Fact sentence → a confirmed ledger claim** (existing invariant, unchanged).
- **Conclusion / argument sentence → a surviving hypothesis + warrant gate** (no longer required to map to a "confirmed fact" — a conclusion is an argument node inferred from multiple claims via a warrant, not a collected fact).
- Mini Assurance: fact sentences against the Claim Ledger; reasoning / conclusion sentences against the Hypothesis Matrix (per §5's warrant checks — the reviewer receives the conclusion sentences and their warrant records explicitly, see `fact-check-protocol.md`).

## 7. Carrying the spine through DR escalation (Step 4 / 6 — the spine's most valuable application)
- **Step 4 (Adjudication)**: the DR prompt carries the **hypothesis set + discriminating questions** — upgrading from "help me dig into X" to "evidence A/B is confirmed; please find evidence that **distinguishes H1/H2**". (When Recon was skipped, there is no surviving set yet — send provisional, explicitly unverified candidates, or ask DR to construct and test them; see SKILL.md Step 6's no-Recon branch.)
- **Step 6**: when DR results reflow, update the Hypothesis Matrix status (not only the Claim Ledger).

## 8. Appendix: example splits by research type (reference only, **not templates**)

> Step 2's facet decomposition should follow "diverge → select on two axes," not slot a type into a template. The list below is only for inspiration while diverging; don't treat it as fixed answers (that makes the model converge on the most typical three-part split and miss unknown angles):
- Market research → size & trends / competitive landscape / consumer profile
- Competitive analysis → feature comparison / pricing model / reputation
- Industry analysis → value chain / technology drivers / regulation
- Tech selection → feature comparison / maturity / lessons learned
