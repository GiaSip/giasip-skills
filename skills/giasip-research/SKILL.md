---
name: giasip-research
description: "Use when the user asks to research, investigate, verify facts with sources, compare competitors, study a market or industry, review literature, prepare an evidence-backed report, decide whether a topic needs external Deep Research, or make an evidence-backed judgment or recommendation. Runs breadth-first Quick Recon, Claim Ledger gating, and an Adjudication Hypothesis Spine when needed. This generated target maps the method onto Claude Code and Codex standalone installs."
---

> ✦ A **GiaSip** generated target · github.com/GiaSip/giasip-skills

# GiaSip Research — Standalone

> Generated from the neutral canonical Research method. Do not edit this target by hand; reconcile changes into the canonical source and rebuild.

## Runtime Contract

Apply the compiled method directly in the current host; do not route through
another Research skill to recover its core workflow.

### Claude Code Runtime Contract

- Use independent SubAgents for recon workers and parallel/background execution when available.
- Use WebSearch for discovery and WebFetch for reading sources; use a browser/fetch fallback only when necessary.
- Keep run IDs, artifact persistence, ledger mutation, synthesis, and delivery in the main session.

### Codex Standalone Runtime Contract

- Inspect the callable collaboration schema before delegating and pass only supported fields.
- Use Codex's available public-web search and page-reading tools.
- Use 2 lightweight workers by default and 3 only for three genuinely orthogonal slices.
- Keep run IDs, artifact persistence, ledger mutation, synthesis, and delivery in the main task.

If worker concurrency is unavailable in either host, execute the selected slices
sequentially and disclose the fallback.

---

# Portable Research

This is the only human-maintained semantic source for the Research method.
Claude Code, Codex, and public GiaSip packages are generated host targets; do not
copy host tool names or invocation syntax back into this file.

> **Portability contract:** “worker” means the current host’s independent task primitive.
> When parallel workers are unavailable, execute the same slices sequentially and disclose
> the fallback. Host-native wrappers define concrete tools, persistence roots, and invocation.

---

## Core Principles

1. **Recon before escalation** — Every research task starts with Quick Recon. 2-5 minutes of initial search helps you decide: deliver directly, or escalate to Deep Research with clear questions. Skipping Recon to submit Deep Research blindly wastes quota
2. **Capability fit first** — When Deep Research is needed, the only criterion for platform selection is "who is best at this type of task," not cost — within your subscribed platforms
3. **Language determines the candidate pool** — Chinese tasks prioritize domestic platforms, English tasks prioritize international platforms, mixed tasks use both
4. **Combination over single (high-stakes only)** — Multi-platform cross-validation is only worth it for high-stakes questions (≥10pp numbers / licenses / policy-legal-financial / AI same-faction claims); for general topics (market/competitive/industry), a single platform + primary source grounding is sufficient — don't burn quota on unnecessary multi-platform runs
5. **Numbers and citations must be verified** — All platforms can hallucinate; always remind the user to spot-check critical information
6. **Quota awareness** — Some platforms have monthly caps (e.g., ChatGPT Plus 25/month); Recon helps you save quota for questions that genuinely need deep digging
7. **Verification priority invariant (core)** — **Primary source / locator grounding > source family convergence > heterogeneous model cross-check**. First determine whether a claim has a ground-truth locator, then decide whether to spend on heterogeneous models. Heterogeneous reviewers **cannot substitute** for missing primary source locators (empirical: 1 model that read the primary source > 3 heterogeneous models guessing from memory). "Evidence source family" (owner/regulator/official/independent/vendor/aggregate) and "reviewer faction family" (cross-faction) are two dimensions — don't conflate them.

---

## Core Flow

### Step 0: Establish the Run Directory (persistence convention, spans the whole flow)

Any task that **enters Recon, or skips Recon to escalate directly to DR**, first fixes a run directory and physically persists all intermediate products — this is the prerequisite for Claim Ledger / Mini Assurance / Deep Research reflow to actually work. Otherwise artifacts live only in session context; one compaction or cross-session gap (the user returns the next day with DR results) loses everything, and Mini Assurance can't get readable raw artifacts, degrading into reading the main session's paraphrased summaries (exactly the evaluator leakage it's meant to prevent).

- **Location**: project research → `<project>/research/<topic>-<YYYY-MM-DD>/`; no project home → `~/research-runs/<topic>-<YYYY-MM-DD>/`
- **Structure**:
  ```
  <run_dir>/
    manifest.md               # run state anchor (cross-session recovery entry, see below)
    artifacts/                # each recon worker facet/gap's full raw output, one .md (incl. 00-discovery.md from Step 2A)
    snapshots/                # normalized main text of critical / high-risk sources, one file per claim_id (Step 2.5)
    quotes.tsv                # externalized input for the quote gate, written before it runs (Step 2.5)
    ledger.md                 # Claim Ledger master table (Step 2.5) + Hypothesis Matrix as an independent section (Adjudication, Step 2.5)
    recon-report.md           # final report for Recon direct delivery
    deep-research-prompt.md   # if escalated: generated DR prompt
    deep-research-raw/        # if escalated: raw reports returned by each platform
    final-report.md           # merged Recon + DR final version
    audit.md                  # Mini Assurance / fact-check audit results
  ```
- **The orchestrator owns path allocation and acceptance; the host runtime may write the bytes**: every Round 1 / Round 2 worker's **full raw output** must land in `<run_dir>/artifacts/<NN>-<facet>.md`, one unique file per worker, at a path the **orchestrator** assigns — never one the worker picks for itself, since self-named files collide and overwrite silently. If the host can direct a worker's output straight to a file — some runtimes expose a per-worker output path plus a file-only output mode — **use it**; do not have the orchestrator re-emit the worker's text merely to "own" the write. Re-transcription costs a full regeneration of the same content — measured at 88KB / 185s = 44% of one run's wall clock, of which >99% was token generation and <1% file I/O.
  - What the orchestrator must **not** delegate: assigning the path, verifying — once every worker has finished, using whatever wait/join primitive the host provides — that each artifact is non-empty and sits at the expected path, and deciding what enters the ledger. An artifact is by definition un-adjudicated raw output — letting the runtime persist it does not promote it to a trusted claim, and it removes one lossy transcription step before the Mini Assurance reviewer reads it.
  - `ledger.md` / `audit.md` / `report.md` stay **orchestrator-written only**.
  - Trade-off to accept knowingly: with direct-to-file output the orchestrator has not read the text before proceeding, so the post-`wait` read-back + non-empty + path check stops being optional. Unbypassable write isolation would need a dedicated artifact-write tool (realpath-checked, write-once) plus removing the worker's shell — a tool-name whitelist never provided it, since a worker holding `bash` can already redirect to any reachable path.
- **Run directory names must carry a random suffix** (`mktemp -d`), not just `<topic>-<date>`: same-topic same-day reruns — regression tests, A/B comparisons, concurrent dispatch — otherwise land in the same directory and overwrite each other **silently**, so half of the resulting report may come from the previous run.
- **manifest.md = cross-session recovery anchor**: `status` (`in_recon` / `awaiting_user_dr` / `delivered` / `partial` / `blocked_needs_approval`) + **research mode (Retrieval/Mapping/Adjudication — so a resumed session knows whether hypotheses need updating when DR returns)** + current step + todos + items awaiting user confirmation. Written when the run is created, updated one line per step change / whenever pausing for the user — so a user returning days later with DR results lets the main session read manifest first to know where it stopped and what it's waiting for.
- **Skip-Recon tasks** (walled-garden / academic review / user directly requests DR): also create the run directory first — build `manifest.md` (`status: awaiting_user_dr` + flag `recon_skipped: true`) + an **empty `ledger.md`**; after DR results return, initialize the ledger per Step 6 (**no nonexistent Recon reconciliation**).
- **Exception**: quick-lookup tasks (user just wants a fast answer, clearly no quality-control loop needed) may skip persistence and deliver inline; but any task that triggers the Claim Ledger Gate / Mini Assurance / possible DR escalation must persist.

### Step 1: Analyze the Research Task

Extract from user input:
- **Research language**: primarily Chinese / primarily English / mixed
- **Research type**: academic/professional / strategic/industry analysis / fact-checking / enterprise data integration / Chinese walled-garden platform data / ultra-long document analysis / sentiment analysis / mixed
- **Depth requirement**: quick lookup (< 10 min) / standard report / deep research
- **Hallucination tolerance**: extremely low (academic/legal/financial/model-license/primary-source verification) / low (tool selection/competitive) / medium (business) / high (exploratory)
- **Citation requirement**: academic-grade (sentence-level tracing) / business-grade / informal
- **Special platform needs**: whether CNKI / Xiaohongshu / WeChat Official Accounts / Twitter, etc. are needed
- **Research mode** (determines whether the Hypothesis Spine engages): **Retrieval** (a single fact / price / list → skip the spine) / **Mapping** (survey / landscape / non-adjudicative comparison → coverage only; **default**) / **Adjudication** (why / evaluation / recommendation / decision — "should we", "which is better" → **fully engage the spine**). **When unsure, default to Mapping**; escalate to Adjudication only when the sub-question **requires comparing plausible options and defending an inferential judgment** (even if the outcome is `underdetermined`); route mixed tasks per sub-question. Full spec: `references/hypothesis-spine.md`.

> **Explicit declaration (required)**: After analysis, state the seven dimensions above — especially **hallucination tolerance + citation requirement + research mode** — in one or two lines before starting. They directly drive fact-check triggering (extremely low + academic-grade), the Round 2 primary-source constraint, and whether the Hypothesis Spine engages (Adjudication); skipping the declaration means re-improvising the judgment at every branch point, rendering the trigger chain moot.

### Step 2: Quick Recon — 2A Discovery Sweep, then 2B Round 1 (Breadth Reconnaissance)

Use the current host's runtime mapping to run initial research, aiming to map the landscape and knowledge gaps within 2-5 minutes.

#### When to Skip Recon

Skip directly to Step 4 (platform matching) in these scenarios:
- User explicitly says "submit to Deep Research directly" or "skip preliminary research"
- The task's core need is **walled-garden platform data** (CNKI / Xiaohongshu / WeChat Official Accounts, etc.) that the current host cannot reach
- The task is an **academic literature review** requiring full papers and citation chains beyond the host's public-web coverage
- The user has already done preliminary research and comes with specific questions

#### Step 2A: Discovery Sweep (harvest names, don't read deeply)

> **Origin**: a 2026-08-21 internal survey lost on **breadth** to a plain chatbox search — it missed the closest competitor's detail and missed an adjacent-category project (58k stars) outright, because every facet keyword was locked to the topic's own name. Verification was never the weak axis; discovery was.

Before facet decomposition, run pure discovery: harvest names, aliases and category words; read nothing deeply, extract no ClaimCards. **Retrieval-mode quick lookups skip 2A.**

**Each round returns exactly these 6 fields** (a fixed schema — an open-ended "search more" instruction is what lets a model declare saturation after one round):

1. `queries_and_tools` — every query issued and where it was issued
2. `new_vocabulary` — aliases and category words **the field itself uses**, not the ones you arrived with
3. `new_entities` — projects / products / papers / organizations / people: name + one line + where found
4. `gaps` — what is visibly still unmapped
5. `negative_results` — `query + index searched + result: 0`. **Required, not optional**: a dry round can only be told apart from a lazy round by what was searched and came back empty
6. `next_queries` — what this round's new vocabulary makes searchable that was not searchable before

**The first round must include all three of:**

- **A named-entity lead list, written before any facet is chosen** — a first-round artifact that names proper nouns: projects, products, papers, organisations, statutes, standards. Not categories, not angles — the actual searchable strings. Produce it from what you already know plus a broad first sweep, and mark it **lead, not evidence**: every name re-enters 2A as a query, and nothing on it may be cited without independent grounding in 2B. **A hallucinated name is cheap only because it gets grounded or dropped — it never becomes a negative result**, since "a thing that never existed was not found" is not a fact about the field and pollutes the ledger if recorded as one
- **Field-native index first** — the field's own registry (code-host search, preprint server, platform API, standards body) outranks generic web search, which returns the SEO layer of a field rather than the field. **Do not run the whole round through one backend**: the failure this step prevents is not "too few queries", it is "every query answered by the same index"
- **The adjacent-category question** — "what else solves this need without being called by this name?" The named category is a keyword, not the boundary of the solution space

> **Why the entity list is an artifact and not a reminder.** Facet selection and entity enumeration draw on the same model, but at different resolutions: facets come out as abstract angles, entities come out as searchable strings. The 2026-08-21 incident is what the distinction costs — the facets were reasonable and *every keyword inside them stayed locked to the topic's own name*. An inline "remember to think of names first" is silently skippable and leaves nothing to check; a file either exists or it does not.
>
> **Baseline assumption: one model and the tools it ships with.** This step must be completable by a host that has exactly one model and web search — that is the only configuration every install is guaranteed. If you also have a second assistant from another vendor, running the same lead pass through it is the highest-value optional addition here, because it brings a different retrieval stack and different ranking, not merely a second opinion. Optional means optional: a run that skips it is fully conformant.

**Stopping rule**: default 2 rounds, hard cap 3. Round 3 opens **only** when round 2 still produced decision-relevant new entries. "Dry" means **no effective new entries** — entries that would change facet selection — not a count of entities: 20 more forks of the same project is a dry round.

**Output**: entity list + alias vocabulary + negative-result record, persisted to `<run_dir>/artifacts/00-discovery.md`. **That file is a coverage record, never evidence** — it holds leads and index listings that were deliberately not read. It is excluded from the artifact set a Mini Assurance reviewer may cite as support (Step 3); a claim traceable only to it is unsupported.

**2A and 2B stay separate.** Merging them ("discover and verify as you go") is what makes a run converge early: the first plausible entity becomes the frame, and everything after it gathers evidence for a frame chosen before the map existed.

#### Step 2B: Round 1 Execution

Break the task into 2-3 **non-overlapping information facets** — drawn from 2A's entity clusters and alias vocabulary when 2A ran — and dispatch one recon worker per facet using the selected runtime mapping. If parallel workers are unavailable, execute the same facet prompts sequentially.

**Facet decomposition = diverge, then select on two axes** (not slotting the research type into a fixed template — templates make the model converge on the most typical three-part split and miss unknown angles):
1. **Diverge**: privately list 4-6 candidate angles (default, not a hard rule; for high-uncertainty / high-risk topics include 1 cross-domain / challenger angle, but no novelty theater).
2. **Select 2-3 that satisfy two orthogonal criteria at once**: ① cover **different decision-relevant unknowns** (non-overlapping) ② point to **different evidence sources / methods** (avoid re-answering the same question with correlated evidence). Selecting only on "different source" makes three workers re-answer one question with different sources.
3. **Name the residual in one line**: state explicitly what these 2-3 facets **do not cover** (at k=2-3 coverage is inherently incomplete; making the residual explicit beats pretending completeness).

> Per-research-type example splits (market / competitive / industry / tech-selection) live in `references/hypothesis-spine.md` — reference examples, **not templates to slot into**.

**Recon worker instruction template:** → See `references/subagent-templates.md` for the full Round 1 template (includes ClaimCard schema, data source hygiene discipline v2.4, and output format).

**Tool selection**: the host's native web search + page reading tools by default (zero additional external quota), falling back to a browser or extraction tool only when the native reader hits JS rendering or anti-scraping blocks — source priority itself is governed by 2A's field-native-index rule and the data source hygiene discipline in the worker template.

### Step 2.5: Claim Ledger Gate + Hypothesis Matrix + Gap Assessment & Round 2 (Conditional)

After all Round 1 workers return, the orchestrator runs a **Claim Ledger Gate** first, then (Adjudication only) forms a **Hypothesis Matrix**, then does gap assessment to decide whether Round 2 is needed.

> **Mode recheck (ALL modes run this — do it before the branch below).** Do the Round 1 findings require **comparing plausible competing answers to the same question** (and are there at least two live candidates)? **Yes** → escalate to Adjudication even if Step 1 tagged Retrieval/Mapping, and build the Hypothesis Matrix section below. **No** → the task stays Retrieval/Mapping and skips the Hypothesis Matrix. (Sources merely *disagreeing on a fact* → that's Claim Ledger conflict arbitration, not Adjudication.) This recheck lives here, above the Adjudication-only section, so a Mapping run cannot skip it and silently miss its own escalation.

#### Claim Ledger Gate (v2.5)

> **Design origin**: Inspired by the claim-level quality control approach from Claude Code Workflow's deep-research skill. Core idea: elevate reliability from "summary-level" to "claim-level," shifting quality control left to the extraction stage — cheaper than catching issues downstream in Mini Assurance.

Consolidate all worker ClaimCards into a single ledger. **Ledger schema** (per entry):
`claim_id / normalized_claim / importance(central/supporting/context) / risk_reason(why high-risk) / source_family(owner/regulator/official/independent/vendor/aggregate/community) / locator(primary source locator) / evidence_kind(quote|locator) / capture_anchor(source_sha256 + retrieved_at) / status(confirmed/weak/unresolved/refuted) / merged_from(repost merge count) / counterquery`

Run through the gate in order:

1. **Merge duplicates** — URL dedup **+ claim-level semantic dedup** (the same number reposted by 5 aggregators ≠ 5 pieces of evidence; merge to 1, record `merged_from`)
2. **Flag high-risk** — `risk_reason` non-empty = high-risk (≥10pp numbers / license / policy-legal-financial / AI same-faction assertions)
3. **Central claims without locator → send back to Round 2** (no evidence-free conclusions allowed). **A locator is not a quote**: a `central` claim whose `evidence_kind` is `locator` caps at `weak` — it can be mentioned, never concluded, because no re-check can ever confirm or refute it mechanically. Same cap when the `capture_anchor` is missing **and unexplained** on a machine-readable source. Missing is *not* proof that nobody opened it — a host may read a page fine yet be unable to expose a hashable full body. So say which it is: record `source_sha256: unavailable` together with a `capture_method` naming how the source was actually read. An explained `unavailable` leaves the claim's normal status intact; an *unexplained* absence caps at `weak`, because nothing then distinguishes it from never having opened the source
   - **Capture discipline for central / high-risk claims**: persist the **normalized main text** to `<run_dir>/snapshots/<claim_id>.txt` at capture time, alongside the hash. A hash with no snapshot behind it cannot be recomputed by anyone later, which is how `unavailable` becomes the inertial default instead of the exception it should be. The goal is a **re-checkable copy of the source text**, not one particular fetch tool: use whatever reader actually yields the full body for that format (HTML reader-mode, PDF text layer, API JSON, raw byte fetch); when a format genuinely yields no body, that is the `unavailable` + `capture_method` case above
4. **Central claims supported only by vendor/aggregate → mark `weak`**, excluded from conclusion topic sentences (can only appear in "pending verification")
5. **Claims with conflicting evidence → selective adversarial verification** (see below, not full-coverage)
6. **Uncertain claims → mark `unresolved`, not `refuted`** (refuted requires explicit conflicting evidence; uncertain ≠ disproven, just not reportable as fact)

**Deterministic quote gate (cheap, runs before any reviewer)**: once snapshots exist, verify every `quote` claim mechanically against its **source snapshot** — never against a worker artifact, which is the audited party restating itself. The orchestrator first writes the claim rows to `<run_dir>/quotes.tsv` (same externalized-input principle as `audit-input.tsv`), tab-separated, header exactly:

```
claim_id	importance	evidence_kind	quote	snapshot	source_sha256	source_url
```

**Column contract, in full** — these rules live in the gate; write them here too, because the orchestrator composes the file from this page, not from the source:

| column | contract |
|---|---|
| `evidence_kind` | exactly `quote` or `locator`. Not a hedge, not a compound ("quote for X + locator for Y") — an implicit kind is what makes an unanchored claim indistinguishable from an unquotable one. |
| `quote` | non-empty for `quote` rows, **including `unavailable:` rows**. An empty string is a substring of everything and would be reported as verified while anchoring nothing. |
| `snapshot` | filename **relative to the snapshots directory** (`<claim_id>.txt`), not relative to the run directory. Empty for `locator` rows. A body that was read but could not be hashed writes `unavailable:<capture_method>` **here, in this column** — not in `source_sha256`. |
| `source_sha256` | the recorded anchor, or the bare word `unavailable` when the snapshot column carries the escape hatch. |

The **claim roster is a separate, mandatory input**: write `<run_dir>/claims-expected.tsv` (one `claim_id` per line) from the ClaimCards **before** composing `quotes.tsv`, and pass it with `--expected`:

```bash
python3 "<skill_dir>/scripts/verify-quotes.py" \
  --run-dir "<run_dir>" --expected "<run_dir>/claims-expected.tsv"
```

**Why the roster is not optional.** Strict row parsing protects *rows*; it cannot protect *coverage*. A `quotes.tsv` holding one valid row is not malformed — so without a roster the gate inspects that row, prints `checked 1 claim(s): 1 quote_ok`, and exits 0 while every other claim goes unexamined. That is the same defect as a self-declared audit count: **the denominator would again come from the party under audit.** The roster is the independent denominator; a claim missing from `quotes.tsv`, an id the roster never declared, or a duplicated id are each a hard input error (exit 2).

The gate refuses to guess: a malformed row is a hard input error (exit 2), never a skipped row — a tolerant Markdown parser drops rows silently, and a dropped row is indistinguishable from a passing one. `locator` rows leave quote/snapshot empty; a quote whose body could be read but not hashed writes `unavailable:<capture_method>` and is reported as `unverifiable_capture` — legitimate, and explicitly **not** verified. **A run in which nothing was machine-checked exits non-zero**, even when every row is individually legitimate: an all-`locator` / all-`unavailable` file is a valid state, but a green gate that checked nothing is precisely the decorative case this script exists to refuse.

Failures are the only items that need a reviewer's attention; a passing quote still owes the ledger and Mini Assurance its *semantic* audit — "the quote is real" is not "the source supports the claim". State the boundary this way and no stronger: **given a snapshot accepted as authoritative**, the quote is a substring of it and the snapshot still hashes to what the ledger recorded. It does not show the snapshot came from that URL, that quote and snapshot were not fabricated together (usually the same worker made both — the defense against that is capturing outside the worker's control), or that extraction was complete. URL reachability (`--check-urls`) is reported separately and is never evidence.

**Selective adversarial verification** (high-risk / conflicting claims only, not full coverage). Strictly follow Principle 7's verification priority invariant through three levels:
- **① Primary source grounding first**: when owner/regulator/official primary sources are directly readable, read the original text to arbitrate — most conflicts resolve here, **no need for heterogeneous models**.
- **② Then source family convergence**: have a skeptic search for counter-evidence across **different evidence source families** (owner / independent test / vendor); arbitrate by **source family**, not by agent vote count (running the same search engine 3 times is just correlated noise).
- **③ Heterogeneous reviewer faction (cross-faction) last**: escalate only when the topic involves AI same-faction content (see Step 3). This is the reviewer/model dimension, **orthogonal to ②'s "evidence source family" — don't conflate**.
- Verdict: explicit conflicting evidence → refuted; insufficient evidence → unresolved (excluded from factual narrative); multi-source-family corroboration → confirmed.

#### ★ Hypothesis Matrix (built when the mode recheck above lands on Adjudication; after breadth + the Claim Ledger Gate, before Round 2)

> The third axis (argument validity — evidential and inferential support, not formal logical validity). **Retrieval / Mapping skip this section.** It converts scattered claims into **evidence-tested** candidate answers — the "information collector → argument engine" step that generic search-and-summarize flows omit. **Hypotheses do NOT enter the Claim Ledger** (to avoid polluting its confirmed/weak semantics and a circular self-justification hole); keep them in a separate section of the same `ledger.md`.

- After breadth returns, converge the findings into **2-3 mutually competing candidate answers** (Chamberlin's multiple working hypotheses), **including one null / status-quo / "not worth doing" hypothesis** (to prevent nominal alternatives that share one hidden assumption). **Form hypotheses after breadth** (to prevent anchoring). Give each a **type-appropriate discriminator** (see hypothesis-spine.md §4).
- Record per hypothesis: `hypothesis_id / candidate_answer / type(causal|decision|forecast) / supporting_claim_ids / contradicting_claim_ids / discriminator_or_falsifier / status(active|conditional|rejected) / revision_history / residual_uncertainty`; and a **matrix-level** `matrix_outcome(preferred|underdetermined|none_of_current)` (+ `preferred_hypothesis_id`). Note `underdetermined` is a matrix outcome, not a per-hypothesis status.
- **Full schema, discrimination discipline, warrant gate, and the Claim-Ledger-vs-Matrix boundary: see `references/hypothesis-spine.md`.**

#### Gap Assessment Logic

> **Design philosophy** (inspired by MiroThinker's Interactive Scaling): one-shot broad search tends to miss key directions. Round 2's value lies in "searching again with Round 1's knowledge" using more precise keywords to fill critical gaps, not repeating Round 1's breadth.

After collecting Round 1 results, check knowledge gaps item by item:

**Round 2 triggers** (any one sufficient):
- **Coverage gap**: Round 1 revealed unexpected new directions / a critical single-source data point affecting core judgment / contradictory workers / a clearly missed angle
- **★ Discrimination gap (Adjudication mode)**: evidence cannot yet **distinguish** competing hypotheses → Round 2 designs a discriminating / disconfirming query (a strong-inference-inspired discrimination pass, "find evidence **against** Hx"), not filling a vague blank

**Skip Round 2 conditions** (any one sufficient to skip):
- **Retrieval/Mapping**: scope audit passes (against ① the user's original explicit ask ② discarded candidate angles ③ a generic-dimension backstop checklist — entities / process / space-time / stakeholders / rival hypotheses — only when a key residual gap remains); **Adjudication**: surviving hypotheses are sufficiently discriminated (**note: fact count ≠ coverage proxy — do NOT use "≥N findings" as a skip criterion**)
- Gap nature requires **walled-garden platforms or academic full text** — Round 2 can't reach them; escalate to Deep Research directly
- User's need is quick-lookup level, Round 1 is sufficient
- Round 1 already consumed significant time (> 5 min), not worth more waiting

> **Precedence when triggers and skip conditions both fire** (ordered): unreachable evidence (walled-garden / academic full text) → escalate to DR; otherwise a material coverage / discrimination gap → Round 2; otherwise skip. A time-budget cutoff yields `partial` (or `underdetermined` for Adjudication) — it does **not** imply the hypotheses were sufficiently discriminated.

#### Round 2 Execution

Unlike Round 1, Round 2 is a **targeted pass**, not a broad sweep:

- Dispatch only **1-2 workers** (not 2-3)
- Each worker targets **one specific gap**, not a broad facet
- Worker instructions **include Round 1's high-confidence findings as context** to avoid re-searching known information
- **Adjudication**: design the query to **discriminate or disconfirm** a surviving hypothesis — the worker prompt says outright "find evidence **against** Hx" (a fresh worker reduces anchoring, but the prompt must still request symmetric treatment of supporting and contrary evidence)

**Additional constraints for high fact-density task types:** When "hallucination tolerance = extremely low" AND "citation requirement = academic-grade", Round 2 must include at least 1 "direct primary source reading" task. → See `references/subagent-templates.md` for primary source types, unit sanity check rules, and the full Round 2 template (includes ledger_patch and, for Adjudication, hypothesis_patch format).

> After Round 2 returns, the main session applies `ledger_patch` back to the master ledger (re-running the gate) to ensure Round 2's critical corrections enter the ledger — otherwise Step 3 Mini Assurance can't see them. **Adjudication mode**: Round 2 also emits `hypothesis_patch` (`update hypothesis_id=... status→...`) to update the Hypothesis Matrix; **absence of evidence ≠ refutation** — only explicit conflicting evidence or a failed predicted observation rejects a hypothesis; a failed search records an `unresolved` **Claim Ledger** entry and leaves the hypothesis status unchanged (never write `unresolved` as a hypothesis status). **Round 2 cap stays at 1 round** (no stopping rule = infinite loop).

### Step 3: Synthesis & Decision

After collecting all Round 1 (and Round 2, if triggered) results, evaluate next steps.

#### Decision Criteria

**Recon is sufficient (deliver directly):**
- **Quality-control invariant, split by sentence type**: **fact sentences → map to one `confirmed` ledger claim** (`weak`/`unresolved` excluded from topic sentences, only in "pending verification"); **conclusion / argument sentences (Adjudication) → map to a surviving hypothesis + pass the warrant gate** — a conclusion is an argument node inferred from multiple facts via a warrant, not required to be a "confirmed fact" itself
- **Warrant gate (load-bearing conclusions only)**: `claim / evidence IDs / warrant (reason) / qualifier / key defeater` — the audit is **not** "are there zero contradicting claims" (a preferred hypothesis may legitimately have some, and requiring zero rewards omission); a fresh reviewer verifies the evidence IDs exist with acceptable ledger status, the warrant sufficiently supports the conclusion, the qualifier matches evidence strength, and **known contrary claims / defeaters are complete and materially addressed (no unaddressed decisive contradiction after a documented countersearch)**; self-evident light conclusions don't need it
- All central metric / license / policy / ≥10pp number claims **have owner/regulator/official/independent-level locators** (not 5 aggregate sites padding the count)
- Remaining gaps involve only peripheral details, not affecting core judgment
- User's need is quick-lookup or standard-report level, no walled-garden data or academic-grade citations required
- **★ Adjudication's legitimate terminal outcomes include `underdetermined`**: when evidence can't decide, **do NOT force a single surviving hypothesis** (forcing = rejecting an un-refuted hypothesis just to fit a format = premature closure); honestly output "multiple hypotheses coexist + the conditions under which each holds + which evidence would decide between them"

→ Compile Recon results directly (merge Round 1 + Round 2), output research report. Jump to Step 5's "Recon direct delivery" template.

**Need Deep Research (escalate):**
- After Round 1 (+ Round 2), critical data points still lack reliable sources
- Major information conflicts discovered, and the current host's web-reachable sources are exhausted
- Obvious knowledge gaps remain, fillable only through walled-garden platforms, academic full text, or deep industry data
- User requests deep-research level

→ Proceed to Step 4 with both rounds of Recon findings, generate a targeted Deep Research prompt. The prompt quality will be higher because "known information" is richer and "questions to deep-dive" are more precise.

**User briefing format:**

```markdown
## Quick Recon Results

### Information Gathered
- [Round 1 + Round 2 core findings summary, 3-7 items]

### Knowledge Gaps
- [Unresolved questions, if any]

### Recommendation
[Deliver directly / Escalate to Deep Research, with rationale]
[If Round 2 was triggered, briefly explain what it filled]
```

**When delivering from Recon (no paid action), don't wait for confirmation** — compile results and output the report directly. But any action consuming external paid quota (DR escalation, or paid fact-check within direct delivery) follows the unified authorization rule below: report cost first, wait for confirmation — no longer distinguishing between the two.

> **Unified external paid-quota authorization rule (covers the whole flow)**: delivering the report itself needs no confirmation, but **any action consuming external paid quota** — DR escalation, the high-fact-density Perplexity DR fact-check, cross-faction reviewers — **always reports "platform + estimated count/cost" first and waits for user confirmation**. Exception: the user has explicitly said "submit directly / no need to ask". This rule takes precedence over any "default run / mandatory" phrasing in the fact-check protocol.

#### Fact-Check Protocol for High Fact-Density Tasks

When "hallucination tolerance = extremely low + citation requirement = academic-grade", reports delivered from Recon **must undergo independent fact-checking** — the orchestrator and the recon workers cannot score themselves. **The mandatory path runs on the host alone**: the deterministic quote gate, primary source locator reading, an independent worker checking primary sources for blind spots, and Mini Assurance. An external Deep Research fact-check and a cross-faction reviewer are **enhancements** — run them when a subscription or a second vendor family is available, and when they are not, label the gap (`fact_check_depth: baseline-only`, `cross_faction: unavailable`) rather than skipping quietly or letting a same-family reviewer stand in. **Cross-faction discipline still governs AI same-faction content** — it decides whether the false-humility dimension can be judged at all, not whether the report ships. **For Adjudication reports, Mini Assurance also audits conclusion sentences against the Hypothesis Matrix** (are the warrant's evidence IDs valid; are known contrary claims / defeaters materially addressed) — not just fact sentences against the ledger. The reviewer receives the conclusion sentences and their warrant records as extracted inputs, not by reading the draft's conclusions section.

→ See `references/fact-check-protocol.md` for the full protocol (Layer 0/1/2 flow, v2.4 cross-faction discipline, conflict arbitration order, empirical cases, and Mini Assurance audit procedure including the Adjudication conclusion-sentence rule).

### Step 4: Match Deep Research Platform

> Only executed when Step 3 determines escalation is needed.

Refer to `references/platform-profiles.md` for each platform's capabilities; refer to `references/matching-rules.md` for matching logic.

Core approach: identify the task's 1-2 most critical requirement dimensions, match the platform strongest on those dimensions. Don't prioritize a platform because it's "free" or "cheap" — pick the most capable.

**★ Adjudication mode: the DR prompt carries the Hypothesis Spine** — not "dig deeper into X," but "evidence A/B is confirmed (confirmed claims); please find evidence that **distinguishes H1/H2**" (carrying the surviving hypothesis set + each one's discriminator). When Recon was skipped there is no surviving set yet — send provisional, explicitly unverified candidates, or ask DR to construct and test them (see Step 6's no-Recon branch). This is the spine's most valuable application: spend the most expensive DR quota on discrimination rather than aimless breadth.

### Step 5: Output Research Plan

Based on Step 3's decision, select the corresponding output template.

---

#### Template A: Recon Direct Delivery

Used when Recon results sufficiently answer the user's question.

**Structure compatibility**: If the task has a dedicated output structure (e.g., 6-section: TL;DR / fact table / conflict verification table / action items / pending confirmation / source annotations), **prioritize the task's structure as the main body**; Template A's "Limitations + For deeper investigation" sections serve as closing. Mixing both is reasonable and doesn't count as template deviation.

> **Adjudication delivery**: lead with the defended judgment (or an honest `underdetermined` + holding conditions), back the load-bearing conclusion with a warrant gate (claim / evidence IDs / warrant / qualifier / key defeater), and summarize the Hypothesis Matrix terminal states. Do not force a single winner when evidence is insufficient.

````markdown
## Research Report: [Topic]

> Based on Quick Recon using the current host's web and worker tools; no external Deep Research platform used.

### Key Findings
[Integrated key findings across facets, structured presentation]

### Data Sources
| Source | URL | Confidence |
|--------|-----|------------|

### Limitations
- [Aspects not covered by Recon]
- [Data timeliness notes]

### For Deeper Investigation
> If you feel any aspect needs more depth, let me know and I can dispatch targeted Deep Research.
````

---

#### Template B: Escalate to Deep Research

Used when external platform deep-diving is needed. **Key difference: the prompt includes only `confirmed`-status Recon findings as "established" background** (weak/unresolved excluded, to avoid DR digging along a wrong anchor), so Deep Research focuses on unknowns.

**No-Recon variant** (skip Recon, submit DR directly): there are no confirmed claims to include — the background section lists only the **user-provided raw constraints**, explicitly tagged `[user input, unverified]`, and **never masquerades as "confirmed through preliminary research"**. Returning DR results always go through Step 6's gate (empty-ledger initialization).

````markdown
## Research Plan

### Quick Recon Summary
> [2-3 sentences summarizing known information and core gaps]

### Recommended Platform: [platform name]

**Why this one:** [1-2 sentences focusing on capability-fit rationale]

**Suggested research prompt:**
```
[topic description]

Background (confirmed through preliminary research — confirmed claims only):
- [Recon confirmed finding 1]
- [Recon confirmed finding 2]
- [Recon confirmed finding 3]

Please focus on these questions (not covered by preliminary research):
1. [knowledge gap 1]
2. [knowledge gap 2]
3. [knowledge gap 3]

[output format / other requirements]
```

**Authorization confirmation (required before submitting, wait for user OK):**
- Platform + estimated count: [e.g., Perplexity DR ×1]
- Estimated cost / quota consumption: [e.g., ~$5, or "1 of ChatGPT DR's 25/month quota"]
- ⏸ Wait for user authorization — if declined, don't submit; mark manifest `blocked_needs_approval`, deliver existing Recon as `partial`

**How to use:**
- [Entry URL/path]
- [Estimated duration]

**Caveats:**
- [Known limitations]
- [Parts requiring manual verification]

### Combination Strategy (if applicable)
| Role | Platform | Sub-task | Rationale |
|------|----------|----------|-----------|

> [How platforms coordinate, why combination is needed]

### Alternative Plan
> [When to use alternative, capability differences vs. primary choice]

### Next Steps
> Once you confirm the plan, say "run it" or "submit research" and I'll generate a dispatch page — one-click copy prompt, one-click open platform, all submissions done in 30 seconds.
> After the DR report returns, run Step 6 (reflow: gate + reconcile + persist).
````

---

### Step 6: Deep Research Result Reflow (closing the escalation loop)

> Whenever DR was escalated (or Recon was skipped for direct DR submission), you **must** run this step after the report returns — otherwise quality control covers only the "no-escalation" half of tasks, leaving the most expensive, highest-stakes half naked.

After the user brings back the DR report (possibly in a new session — **read `<run_dir>/manifest.md` first to restore run state**, then continue from ledger.md + artifacts/):

1. **Persist**: store the raw report at `<run_dir>/deep-research-raw/<platform>.md`
2. **Gate**: extract central / high-risk claims from the DR report into ClaimCards, run them through Step 2.5's Claim Ledger Gate (same schema, risk flags, locator requirements) — DR platforms hallucinate too; "paid depth" doesn't exempt them
3. **Reconcile**: align item-by-item against the Recon ledger; conflicts follow the existing Step 2.5 / Step 3 arbitration order (**primary source reading > source family convergence > heterogeneous reviewer**); DR conclusions **don't automatically override** Recon's existing primary-source grounding
4. **★ Update hypotheses (Adjudication)**: after DR reflows, use `hypothesis_patch` to update the Hypothesis Matrix status (which hypothesis DR evidence distinguished / rejected / turned conditional, and the matrix-level outcome), not just the Claim Ledger
5. **Merge & persist**: produce `<run_dir>/final-report.md`, fact sentences mapping to `confirmed` ledger claims and conclusion sentences mapping to surviving hypotheses + warrant gate (same split as Step 3)
6. **Skip-Recon tasks** (walled-garden / academic review, etc.): `ledger.md` starts empty — DR results directly extract ClaimCards to **initialize** the Claim Ledger; there is no Recon ledger to reconcile against, so **skip reconciliation** and run the gate on the DR-seeded claims. **For Adjudication**, the candidates sent in Step 4 were provisional/unverified, so **form the initial Hypothesis Matrix from the gated DR evidence** (don't treat the provisional set as established), then merge. Not exempt from quality control for "having skipped Recon"

> **manifest state transitions** (minimal set, not a full state machine): escalate DR → `awaiting_user_dr`; user declines paid authorization → `blocked_needs_approval`; budget/time exhausted → `partial`; final delivery → `delivered`. Update one line per transition.

---

## Detailed Reference

- `references/hypothesis-spine.md` — Adjudication third axis: research modes, Hypothesis Matrix schema, discrimination discipline, warrant gate
- `references/platform-profiles.md` — Deep Research platform capability profiles
- `references/matching-rules.md` — Platform matching logic and decision tree
- `references/fact-check-protocol.md` — Fact-check protocol (v2.2+v2.4) + Mini Assurance audit (incl. Adjudication conclusion-sentence rule)
- `references/subagent-templates.md` — recon worker instruction templates (Round 1 + Round 2, incl. hypothesis_patch) + unit sanity check
