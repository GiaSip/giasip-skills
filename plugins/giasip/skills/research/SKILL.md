---
name: research
description: "Use when the user asks to research, investigate, verify facts with sources, compare competitors, study a market or industry, review literature, prepare an evidence-backed report, or decide whether a topic needs external Deep Research. Supports English, Chinese, Claude Code, and Codex. Differs from generic search-and-summarize skills: every claim is captured as a ClaimCard with a confidence rating and a source-family tag, and unsupported claims are kept out of conclusions by a Claim Ledger gate."
---

> ✦ A **GiaSip** skill · part of the `giasip` toolkit · github.com/GiaSip

# GiaSip Research — Cross-Runtime Research Orchestrator

You are a **research dispatcher**. Run a Quick Recon with the current host's native web and worker tools, map the landscape and knowledge gaps, then decide whether an external Deep Research platform is needed — and if so, generate a precisely focused prompt for it.

## Core Principles

1. **Recon before escalation** — Every research task starts with Quick Recon. 2-5 minutes of initial search helps you decide: deliver directly, or escalate to Deep Research with clear questions. Skipping Recon to submit Deep Research blindly wastes quota
2. **Capability fit first** — When Deep Research is needed, the only criterion for platform selection is "who is best at this type of task," not cost — within your subscribed platforms
3. **Language determines the candidate pool** — Chinese tasks prioritize domestic platforms, English tasks prioritize international platforms, mixed tasks use both
4. **Combination over single (high-stakes only)** — Multi-platform cross-validation is only worth it for high-stakes questions (≥10pp numbers / licenses / policy-legal-financial / AI same-faction claims); for general topics (market/competitive/industry), a single platform + primary source grounding is sufficient — don't burn quota on unnecessary multi-platform runs
5. **Numbers and citations must be verified** — All platforms can hallucinate; always remind the user to spot-check critical information
6. **Quota awareness** — Some platforms have monthly caps (e.g., ChatGPT Plus 25/month); Recon helps you save quota for questions that genuinely need deep digging
7. **Verification priority invariant (core)** — **Primary source / locator grounding > source family convergence > heterogeneous model cross-check**. First determine whether a claim has a ground-truth locator, then decide whether to spend on heterogeneous models. Heterogeneous reviewers **cannot substitute** for missing primary source locators (empirical: 1 model that read the primary source > 3 heterogeneous models guessing from memory). "Evidence source family" (owner/regulator/official/independent/vendor/aggregate) and "reviewer faction family" (cross-faction) are two dimensions — don't conflate them.

---

## Runtime Adapter

Apply one host mapping. Keep the research method below unchanged.

### Claude Code runtime

- Use Claude Code SubAgents for independent recon workers; use parallel/background execution when the host exposes it.
- Use `WebSearch` for discovery and `WebFetch` for reading sources. Use a browser/fetch fallback only when those tools cannot read the page.
- Keep synthesis, ledger mutation, artifact persistence, and the final answer in the main session.

### Codex runtime

- Inspect the current callable schema before using `spawn_agent`. Pass only fields the host actually exposes; put the slice, read-only scope, source expectations, and ClaimCard contract in the worker message.
- Use Codex's available web search/open tools. Do not emit Claude-only tool calls or claim a model/effort override unless the host accepted it.
- Use 2 lightweight workers by default; use 3 only when the topic naturally has three non-overlapping slices. Keep final synthesis and conflict resolution in the main thread.
- If `spawn_agent` is unavailable or the thread limit is reached, run the slices sequentially and state that no parallel workers were used.

### Shared worker contract

- Workers collect evidence and return ClaimCards; the orchestrator owns run IDs, artifact persistence, ledger updates, synthesis, and delivery.
- Treat worker completion as evidence collection, not as permission to copy its prose into the final answer without the Claim Ledger Gate.
- Internal read-only workers do not require an extra confirmation unless the host policy or user instruction requires one. Paid external research always follows the authorization rule in Step 3.

### Bundled references

All reference paths are relative to this `SKILL.md` and ship inside the same installed skill directory. Read them only when the matching branch is reached:

- Before dispatching Recon workers: `references/subagent-templates.md`
- For high-risk fact-checking or Mini Assurance: `references/fact-check-protocol.md`
- Before recommending external Deep Research: `references/matching-rules.md` and `references/platform-profiles.md`

---

## Core Flow

### Step 0: Establish the Run Directory (persistence convention, spans the whole flow)

Any task that **enters Recon, or skips Recon to escalate directly to DR**, first fixes a run directory and physically persists all intermediate products — this is the prerequisite for Claim Ledger / Mini Assurance / Deep Research reflow to actually work. Otherwise artifacts live only in session context; one compaction or cross-session gap (the user returns the next day with DR results) loses everything, and Mini Assurance can't get readable raw artifacts, degrading into reading the main session's paraphrased summaries (exactly the evaluator leakage it's meant to prevent).

- **Location**: project research → `<project>/research/<topic>-<YYYY-MM-DD>/`; no project home → `~/research-runs/<topic>-<YYYY-MM-DD>/`
- **Structure**:
  ```
  <run_dir>/
    manifest.md               # run state anchor (cross-session recovery entry, see below)
    artifacts/                # each recon worker facet/gap's full raw output, one .md
    ledger.md                 # Claim Ledger master table (maintained in Step 2.5)
    recon-report.md           # final report for Recon direct delivery
    deep-research-prompt.md   # if escalated: generated DR prompt
    deep-research-raw/        # if escalated: raw reports returned by each platform
    final-report.md           # merged Recon + DR final version
    audit.md                  # Mini Assurance / fact-check audit results
  ```
- **Persistence is the orchestrator's responsibility, not the worker's**: after each Round 1 or Round 2 worker returns, the orchestrator immediately writes its **full raw output** to `<run_dir>/artifacts/<facet>.md` — persisting the untransformed original so the Mini Assurance reviewer reads the artifact itself.
- **manifest.md = cross-session recovery anchor**: `status` (`in_recon` / `awaiting_user_dr` / `delivered` / `partial` / `blocked_needs_approval`) + current step + todos + items awaiting user confirmation. Written when the run is created, updated one line per step change / whenever pausing for the user — so a user returning days later with DR results lets the main session read manifest first to know where it stopped and what it's waiting for.
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

> **Explicit declaration (required)**: After analysis, state the six dimensions above — especially **hallucination tolerance + citation requirement** — in one or two lines before starting. They directly drive fact-check triggering (extremely low + academic-grade) and the Round 2 primary-source constraint; skipping the declaration means re-improvising the judgment at every branch point, rendering the trigger chain moot.

### Step 2: Quick Recon — Round 1 (Breadth Reconnaissance)

Use the current host's runtime mapping to run initial research, aiming to map the landscape and knowledge gaps within 2-5 minutes.

#### When to Skip Recon

Skip directly to Step 4 (platform matching) in these scenarios:
- User explicitly says "submit to Deep Research directly" or "skip preliminary research"
- The task's core need is **walled-garden platform data** (CNKI / Xiaohongshu / WeChat Official Accounts, etc.) that the current host cannot reach
- The task is an **academic literature review** requiring full papers and citation chains beyond the host's public-web coverage
- The user has already done preliminary research and comes with specific questions

#### Round 1 Execution

Break the task into 2-3 **non-overlapping information facets** and dispatch one recon worker per facet using the selected runtime mapping. If parallel workers are unavailable, execute the same facet prompts sequentially.

**Facet decomposition examples:**

| Research Type | Facet 1 | Facet 2 | Facet 3 (optional) |
|---------------|---------|---------|---------------------|
| Market research | Market size & growth trends | Key players & competitive landscape | Consumer profile / policy environment |
| Competitive analysis | Feature comparison | Pricing & business models | User reviews & reputation |
| Industry analysis | Value chain structure | Technology trends & drivers | Regulation & policy |
| Tech selection | Candidate feature comparison | Community activity & maturity | Real-world cases / lessons learned |

**Recon worker instruction template:** → See `references/subagent-templates.md` for the full Round 1 template (includes ClaimCard schema, data source hygiene discipline v2.4, and output format).

**Tool selection:**
- **Primary**: the host's native web search + page reading tools — zero additional external quota
- **Fallback**: a browser or extraction tool only when the native reader hits JS rendering or anti-scraping blocks

### Step 2.5: Claim Ledger Gate + Gap Assessment & Round 2 (Conditional)

After all Round 1 workers return, the orchestrator runs a **Claim Ledger Gate** first, then does gap assessment to decide whether Round 2 is needed.

#### Claim Ledger Gate (v2.5)

> **Design origin**: Inspired by the claim-level quality control approach from Claude Code Workflow's deep-research skill. Core idea: elevate reliability from "summary-level" to "claim-level," shifting quality control left to the extraction stage — cheaper than catching issues downstream in Mini Assurance.

Consolidate all worker ClaimCards into a single ledger. **Ledger schema** (per entry):
`claim_id / normalized_claim / importance(central/supporting/context) / risk_reason(why high-risk) / source_family(owner/regulator/official/independent/vendor/aggregate/community) / locator(primary source locator) / status(confirmed/weak/unresolved/refuted) / merged_from(repost merge count) / counterquery`

Run through the gate in order:

1. **Merge duplicates** — URL dedup **+ claim-level semantic dedup** (the same number reposted by 5 aggregators ≠ 5 pieces of evidence; merge to 1, record `merged_from`)
2. **Flag high-risk** — `risk_reason` non-empty = high-risk (≥10pp numbers / license / policy-legal-financial / AI same-faction assertions)
3. **Central claims without locator → send back to Round 2** (no evidence-free conclusions allowed)
4. **Central claims supported only by vendor/aggregate → mark `weak`**, excluded from conclusion topic sentences (can only appear in "pending verification")
5. **Claims with conflicting evidence → selective adversarial verification** (see below, not full-coverage)
6. **Uncertain claims → mark `unresolved`, not `refuted`** (refuted requires explicit conflicting evidence; uncertain ≠ disproven, just not reportable as fact)

**Selective adversarial verification** (high-risk / conflicting claims only, not full coverage). Strictly follow Principle 7's verification priority invariant through three levels:
- **① Primary source grounding first**: when owner/regulator/official primary sources are directly readable, read the original text to arbitrate — most conflicts resolve here, **no need for heterogeneous models**.
- **② Then source family convergence**: have a skeptic search for counter-evidence across **different evidence source families** (owner / independent test / vendor); arbitrate by **source family**, not by agent vote count (running the same search engine 3 times is just correlated noise).
- **③ Heterogeneous reviewer faction (cross-faction) last**: escalate only when the topic involves AI same-faction content (see Step 3). This is the reviewer/model dimension, **orthogonal to ②'s "evidence source family" — don't conflate**.
- Verdict: explicit conflicting evidence → refuted; insufficient evidence → unresolved (excluded from factual narrative); multi-source-family corroboration → confirmed.

#### Gap Assessment Logic

> **Design philosophy** (inspired by MiroThinker's Interactive Scaling): one-shot broad search tends to miss key directions. Round 2's value lies in "searching again with Round 1's knowledge" using more precise keywords to fill critical gaps, not repeating Round 1's breadth.

After collecting Round 1 results, check knowledge gaps item by item:

**Round 2 triggers** (any one sufficient):
- Round 1 revealed **unexpected new directions** not covered by original facets
- Critical data points have only a single source, and that data point affects core judgment
- Multiple workers reported **contradictory information** requiring cross-validation
- Round 1 search keywords clearly missed an important angle (in hindsight, better keywords were available)

**Skip Round 2 conditions** (any one sufficient to skip):
- Round 1 high-confidence findings ≥ 5, and gaps only involve peripheral details
- Gap nature requires **walled-garden platforms or academic full text** — Round 2 can't reach them; escalate to Deep Research directly
- User's need is quick-lookup level, Round 1 is sufficient
- Round 1 already consumed significant time (> 5 min), not worth more waiting

#### Round 2 Execution

Unlike Round 1, Round 2 is **precision strike**, not broad sweep:

- Dispatch only **1-2 workers** (not 2-3)
- Each worker targets **one specific gap**, not a broad facet
- Worker instructions **include Round 1's high-confidence findings as context** to avoid re-searching known information

**Additional constraints for high fact-density task types:** When "hallucination tolerance = extremely low" AND "citation requirement = academic-grade", Round 2 must include at least 1 "direct primary source reading" task. → See `references/subagent-templates.md` for primary source types, unit sanity check rules, and the full Round 2 template (includes ledger_patch format).

> After Round 2 returns, the main session applies `ledger_patch` back to the master ledger (re-running the gate) to ensure Round 2's critical corrections enter the ledger — otherwise Step 3 Mini Assurance can't see them.

### Step 3: Synthesis & Decision

After collecting all Round 1 (and Round 2, if triggered) results, evaluate next steps.

#### Decision Criteria

**Recon is sufficient (deliver directly):**
- **Every topic sentence in the report maps to a `confirmed` ledger claim** (`weak`/`unresolved` excluded from topic sentences, only in "pending verification")
- All central metric / license / policy / ≥10pp number claims **have owner/regulator/official/independent-level locators** (not 5 aggregate sites padding the count)
- Remaining gaps involve only peripheral details, not affecting core judgment
- User's need is quick-lookup or standard-report level, no walled-garden data or academic-grade citations required

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

When "hallucination tolerance = extremely low + citation requirement = academic-grade", reports delivered from Recon **must undergo independent fact-checking**. The protocol uses a three-layer approach: primary source locator reading first → Perplexity Deep Research → independent worker blind-spot check, with cross-faction discipline for AI same-faction content.

→ See `references/fact-check-protocol.md` for the full protocol (Layer 0/1/2 flow, v2.4 cross-faction discipline, conflict arbitration order, empirical cases, and Mini Assurance audit procedure).

### Step 4: Match Deep Research Platform

> Only executed when Step 3 determines escalation is needed.

Refer to `references/platform-profiles.md` for each platform's capabilities; refer to `references/matching-rules.md` for matching logic.

Core approach: identify the task's 1-2 most critical requirement dimensions, match the platform strongest on those dimensions. Don't prioritize a platform because it's "free" or "cheap" — pick the most capable.

### Step 5: Output Research Plan

Based on Step 3's decision, select the corresponding output template.

---

#### Template A: Recon Direct Delivery

Used when Recon results sufficiently answer the user's question.

**Structure compatibility**: If the task has a dedicated output structure (e.g., 6-section: TL;DR / fact table / conflict verification table / action items / pending confirmation / source annotations), **prioritize the task's structure as the main body**; Template A's "Limitations + For deeper investigation" sections serve as closing. Mixing both is reasonable and doesn't count as template deviation.

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
4. **Merge & persist**: produce `<run_dir>/final-report.md`, every topic sentence still mapping to a `confirmed` ledger claim
5. **Skip-Recon tasks** (walled-garden / academic review, etc.): `ledger.md` starts empty — DR results directly extract ClaimCards to **initialize** the ledger (no Recon to reconcile), then go through steps 2-4, not exempt from quality control for "having skipped Recon"

> **manifest state transitions** (minimal set, not a full state machine): escalate DR → `awaiting_user_dr`; user declines paid authorization → `blocked_needs_approval`; budget/time exhausted → `partial`; final delivery → `delivered`. Update one line per transition.

---

## Detailed Reference

- `references/platform-profiles.md` — Deep Research platform capability profiles
- `references/matching-rules.md` — Platform matching logic and decision tree
- `references/fact-check-protocol.md` — Fact-check protocol (v2.2+v2.4) + Mini Assurance audit
- `references/subagent-templates.md` — recon worker instruction templates (Round 1 + Round 2) + unit sanity check
