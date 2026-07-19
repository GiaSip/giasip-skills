# giasip-skills

![Version](https://img.shields.io/badge/version-1.6.1-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Code](https://img.shields.io/badge/claude--code-compatible-orange)
![Codex](https://img.shields.io/badge/codex-compatible-black)

> **`giasip-research` runs every finding through a Claim Ledger** — an auditable record where each claim, first captured as a ClaimCard, carries an explicit **confidence rating** and a **source-family tag** (owner / regulator / official / independent / vendor / aggregate / community). A chain of adversarial gates **keeps unsupported claims out of your conclusions**, so this evidence-grounded skill answers not just "what did I find," but "how much should you trust each claim." **For decision and "why" questions it goes a step further** — forming competing hypotheses (including a null), hunting for evidence *against* them, and delivering a warrant-gated judgment (or an honest "undetermined") instead of a pile of facts. One research method, mapped onto Claude Code and Codex.
>
> The repo also ships **`giasip-dispatch`**, a multi-model dispatcher for routing tasks to Codex / Gemini / Kimi / DeepSeek / Doubao / Qwen / GLM / MiniMax.

| Skill | What it gives you |
|-------|-------------------|
| **giasip-research** | A research orchestrator that grounds every claim in evidence. It runs a breadth-first Quick Recon with your host's native workers and web tools, records each finding as a **ClaimCard** (confidence + source family + "what the source said vs. what I inferred"), passes them through a **Claim Ledger Gate** that bars unsupported claims from your conclusions, and escalates to a paid Deep Research platform only when the task needs it — asking before it spends, then re-gating whatever the paid run returns instead of trusting it. Runs persist to disk, so a long research task resumes across sessions. An independent fact-check protocol and a fresh-reviewer audit (on by default for direct-delivery research) keep it honest. For decision / adjudication tasks ("should we A or B," "why Y") it engages a **Hypothesis Spine** — competing hypotheses (incl. a null) → a second round that hunts for counter-evidence → a warrant-gated or honestly `underdetermined` conclusion, instead of piling up facts. |
| **giasip-dispatch** | A multi-model dispatcher — sends a task or prompt to other AI models (Codex / Gemini / Kimi / DeepSeek / Doubao / Qwen / GLM / MiniMax) and retrieves results. **Start with one aggregator key** (OpenRouter overseas / SiliconFlow in China) instead of signing up per vendor. Includes complexity-routing guidelines (API vs CLI vs SubAgent, single vs multi), but the final model choice is left to your agent's judgment. |

---

## Why giasip-research is different

The scarce thing in AI research isn't retrieval breadth — every agent can search. It's two things: **knowing how much to trust each claim**, and — for decision questions — **knowing which answer the evidence actually supports.** This skill is built around both.

> _Compared to typical search-and-summarize **skills** — not to Deep Research platforms, which giasip-research **orchestrates** rather than competes with._

| | Generic research skill | **giasip-research** |
|---|---|---|
| **What backs each fact** | Nothing — facts melt into prose | Each fact recorded as a ClaimCard (confidence + source family) and audited through a Claim Ledger |
| **Provenance** | "I found some sources" | Every claim tagged `owner` / `regulator` / `official` / `independent` / `vendor` / `aggregate` / `community` |
| **Unsupported claims** | Flow through into the summary | Bounced back, or marked `weak` and quarantined out of conclusion sentences |
| **Verification order** | Trust the model | Primary-source grounding **>** source-family convergence **>** cross-model check |
| **Same-family bias** | Unchecked | Cross-faction fact-check when the topic touches the model's own camp |
| **Decision / "why" questions** | Piles up facts, leaves you to judge | Competing hypotheses (incl. a null) → seeks *disconfirming* evidence → a warrant-gated judgment, or an honest `underdetermined` |

You still receive a readable report — the ClaimCards and Claim Ledger are the audit trail *behind* it, not what lands on your desk.

### What a claim looks like

Instead of an unsourced sentence buried in a paragraph, each fact becomes a structured, auditable card:

```yaml
claim_id: r0716-market-A1
claim: "The EU AI Act's GPAI obligations apply from 2 August 2025."
importance: central
claim_type: factual
source_url: https://eur-lex.europa.eu/eli/reg/2024/1689/oj   # primary source
source_type: regulator          # not an aggregator or blog
evidence: "Art. 113(b) — locator: OJ text, applicability section"
source_says_vs_agent_infers:
  source_says: "applies from 2 August 2025"
  agent_infers: "GPAI providers must comply by that date"
confidence: high
gap: "no consolidated English text of the delegated timeline yet"
counterquery: "EU AI Act GPAI obligations start date delayed 2025"
```

The **Claim Ledger Gate** then enforces one rule your conclusions depend on: a `central` claim with **no primary-source locator is sent back for another search round**, and a claim backed only by aggregators or vendor self-reports is marked `weak` and moved to a "to be verified" list — it cannot appear in a conclusion sentence.

### The verification order most agents get backwards

Multi-model cross-checking is widely treated as the gold standard. giasip-research ranks it **last**:

> **primary-source grounding  >  source-family convergence  >  cross-model cross-check**

One model that actually read the primary source beats three models cross-checking each other from memory. Heterogeneous reviewers catch blind spots — they don't substitute for a primary source nobody read. And when a topic touches the reviewing model's own camp, a **cross-faction** model casts the deciding vote.

→ Full method & its lineage: **[The Claim Ledger Method](docs/claim-ledger-method.md)** · see it in action: **[worked example](examples/)**

---

## One ledger, end to end

The Claim Ledger isn't only for the cheap first pass — the **same ledger governs the whole research supply chain**, including the expensive parts. That is what makes this an *orchestrator* rather than another search box.

- **Recon before you spend.** By default a short in-house recon runs first, and a paid Deep Research platform is brought in only for gaps native search can't reach (you can also point it straight at Deep Research when you already know that's what you need). Either way it reports the platform and expected cost and waits for approval — unless you've told it to submit without asking.
- **Only confirmed claims seed the paid run.** When it does escalate, the Deep Research prompt is built from `confirmed` ledger claims only — `weak` and `unresolved` ones are left out, so the paid run isn't sent chasing an unverified anchor.
- **Returned Deep Research is re-gated, not trusted.** The report that comes back is not pasted in. Its claims are extracted into the same ClaimCards, run through the same gate, and reconciled against the recon ledger — a paid platform hallucinates too, and doesn't get a pass for being expensive.
- **Pick up where you left off.** A Deep Research run can take an hour; you often return the next day. Each run persists its ledger, raw artifacts, and a `manifest` state file, so a new session resumes exactly where the last one stopped.

The through-line: **a claim is the one accounting unit from the first cheap search to the last paid report.**

> **Standing on prior art.** Two of the moves are borrowed on purpose: claim-level quality control follows the deep-research skill in Claude Code Workflow, and the targeted second search round follows [MiroThinker](https://github.com/MiroMindAI/MiroThinker)'s Interactive Scaling. What giasip-research adds on top is the ledger *economics* — confirmed-only seeding, re-gated reflow, cross-session persistence — and the source-family verification order.

---

## From facts to a defended judgment

The Claim Ledger tells you *how much to trust each fact*. But for **decision and "why" questions**, a pile of trustworthy facts still isn't an answer — you need to know which conclusion they actually support. That is the **Hypothesis Spine** (added in v1.6.0), a third axis on top of coverage and factual certainty.

- **It only turns on when it should.** Look-up and landscape-mapping tasks skip it entirely — no rigidity added. It engages for *adjudication* tasks ("should we do X," "A or B," "why Y"), with a two-stage recheck so a decision question that was mis-classified as a lookup still escalates.
- **Competing hypotheses, including a null.** After the breadth pass, the findings are converged into 2-3 rival candidate answers — one of them always a null / status-quo / "not worth it" option, so the framing isn't quietly rigged toward acting.
- **Falsification, not confirmation.** The targeted second round hunts for evidence *against* the surviving hypotheses (strong-inference-inspired), not more evidence for them. "Not found" is recorded as unresolved — absence of evidence never counts as disproof.
- **A warrant-gated conclusion — or an honest "undetermined."** A load-bearing conclusion ships with its evidence, its reasoning, and its **key defeater** — the specific thing that would overturn it. When the evidence can't decide, the skill returns `underdetermined` and names what's missing, instead of forcing a single winner.
- **Hypotheses never pollute the ledger.** They live in a separate section from the Claim Ledger, so "a hypothesis that's still standing" is never mistaken for "a confirmed fact."

→ Full spec: **[references/hypothesis-spine.md](skills/giasip-research/references/hypothesis-spine.md)**

---

## Quick Start

1. **Install Research for your host**:
   ```bash
   # Claude Code
   npx skills add GiaSip/giasip-skills --global --skill giasip-research --agent claude-code --yes

   # Codex
   npx skills add GiaSip/giasip-skills --global --skill giasip-research --agent codex --yes

   # Or install the namespaced Codex Plugin
   codex plugin marketplace add GiaSip/giasip-skills
   codex plugin add giasip@giasip-skills
   ```

2. **Try it**:
   - Claude Code: `/giasip-research Research the current state of humanoid robot regulations`
   - Codex: `$giasip-research Research the current state of humanoid robot regulations`
   - Codex Plugin: `$giasip:research Research the current state of humanoid robot regulations`
   - Or simply describe the research task in either host.

---

## FAQ

**How is this different from just asking Claude to research something?**
A raw model produces confident prose whether or not the facts are grounded. giasip-research separates what a source actually said from what the agent inferred, tags each claim's source family, and structurally refuses to promote unsupported claims into conclusions.

**What about decision or recommendation questions ("should we A or B," "why Y")?**
Those trigger the **Hypothesis Spine**: instead of returning a pile of facts, the skill forms 2-3 competing hypotheses (including a null option), runs a second search round that specifically hunts for evidence *against* them, and delivers a conclusion backed by a warrant — its evidence, its reasoning, and the one thing that would overturn it. If the evidence can't decide, it returns `underdetermined` and names what's missing, rather than forcing a pick. Fact-lookup and landscape-mapping tasks skip this automatically, so it never adds overhead where it isn't needed.

**Does it cost money to run?**
Near-zero external dependencies — the Quick Recon uses your host's native web tools. It escalates to a paid Deep Research platform only when the task needs it (a gap native search can't fill, a restricted-platform or academic source, or a high-stakes fact-check) — and it always reports the platform + expected cost and asks before spending.

**Which hosts and languages does it support?**
Claude Code and Codex, running one shared research method with thin runtime mappings. English and Chinese.

**These gates are prompt rules — can't the model just ignore them?**
That's why the final check isn't a prompt. On direct-delivery research, a *fresh reviewer* sub-agent — with its own context — re-reads the raw evidence artifacts (not the model's summary) and labels each conclusion `supported` / `unverifiable` / `conflict`. Reading the raw evidence instead of the model's own write-up is what catches "plausible but unsupported" claims.

**Does it actually improve accuracy?**
We don't publish a benchmark number. In a small number of internal cases the gated pipeline produced noticeably fewer unsupported claims than the same pipeline with the gates off — but that's an internal observation, not a public benchmark and not a claim about other tools. The honest takeaway isn't a number — it's that unsupported statements are *structurally harder* to reach your conclusions, because the Claim Ledger Gate and a fresh-reviewer audit sit between the evidence and the conclusion.

---

## Installation

Choose one Codex distribution mode. Installing both is supported, but normally unnecessary.

### Option 1: Standalone skill with `npx skills add`

```bash
# Claude Code: install all skills globally
npx skills add GiaSip/giasip-skills --global --skill '*' --agent claude-code --yes

# Claude Code: install GiaSip Research only
npx skills add GiaSip/giasip-skills --global --skill giasip-research --agent claude-code --yes

# Codex: install GiaSip Research only
npx skills add GiaSip/giasip-skills --global --skill giasip-research --agent codex --yes

# List available skills in this repo
npx skills add GiaSip/giasip-skills -l
```

Standalone invocation: `/giasip-research` in Claude Code or `$giasip-research` in Codex.

### Option 2: Codex Plugin with the GiaSip namespace

```bash
codex plugin marketplace add GiaSip/giasip-skills
codex plugin add giasip@giasip-skills
```

Plugin invocation: `$giasip:research`.

The Codex Plugin intentionally bundles Research only. `giasip-dispatch` is not bundled because it remains Claude Code-native. See [Codex Plugin architecture and maintenance](docs/CODEX-PLUGIN.md).

### Option 3: Claude Code plugin (Claude Code only)

```
/plugin marketplace add GiaSip/giasip-skills
/plugin install giasip-skills@giasip-skills
```

### Option 4: git clone and copy

```bash
git clone https://github.com/GiaSip/giasip-skills
# Claude Code
cp -R giasip-skills/skills/giasip-research ~/.claude/skills/giasip-research
cp -R giasip-skills/skills/giasip-dispatch ~/.claude/skills/giasip-dispatch

# Codex / Agent Skills-compatible hosts
cp -R giasip-skills/skills/giasip-research ~/.agents/skills/giasip-research
```

> Both standalone and plugin installs use the same Research behavior — only the invocation surface changes:
> - **Standalone** (Options 1 & 4): `/giasip-research` in Claude Code, `$giasip-research` in Codex; `giasip-dispatch` is `/giasip-dispatch` in Claude Code.
> - **Codex Plugin** (Option 2): `$giasip:research`.
> - **Claude Code plugin** (Option 3): skills are namespaced by the plugin — `/giasip-skills:giasip-research` and `/giasip-skills:giasip-dispatch`.

## Distribution Structure

```
skills/giasip-research/                   # Generated standalone Claude/Codex target
├── SKILL.md
├── BUILD-PROVENANCE.json                 # Canonical source hashes + semantic contract
├── agents/openai.yaml                    # Standalone Agent Skills metadata
└── references/

plugins/giasip/                           # Codex Plugin package
├── .codex-plugin/plugin.json
├── BUILD-PROVENANCE.json
└── skills/research/                       # Generated Codex-native target

.agents/plugins/marketplace.json          # Repo marketplace for Codex
scripts/sync_codex_plugin.py              # Neutral canonical → both targets sync/check
skills/giasip-dispatch/                   # Claude Code-native dispatcher
```

---

## giasip-research — Dependencies

**Near-zero external dependencies — works out of the box.** It maps the same research method onto Claude Code's `WebSearch` / `WebFetch` / SubAgents or Codex's available web tools / `spawn_agent`. If worker concurrency is unavailable, the skill explicitly falls back to sequential facets instead of silently skipping coverage.

The only setup needed: fill in the platform availability table in `skills/giasip-research/references/platform-profiles.md` with your actual Deep Research subscriptions (ChatGPT / Gemini / Perplexity / Kimi, etc.) — the matching logic uses this to skip unsubscribed platforms.

## giasip-dispatch — Dependencies

Pick the path that fits. **Most users want the easy path — one aggregator key, no per-vendor signup.**

### 1. Easy path — one aggregator key (recommended)

One key routes to many models through an OpenAI-compatible aggregator. Choose by region, drop **one** `.env` in `~/.config/ai-keys/`, set the provider once, and every alias your chosen provider supports just works.

| Region | Provider | File | Content | Covers |
|--------|----------|------|---------|--------|
| Overseas | **OpenRouter** | `openrouter.env` | `export OPENROUTER_API_KEY=...` | DeepSeek / Qwen / GLM / Kimi / MiniMax **+ Claude / GPT / Gemini** |
| China | **SiliconFlow** 硅基流动 | `siliconflow.env` | `export SILICONFLOW_API_KEY=...` | DeepSeek / Qwen / GLM / Kimi / MiniMax |

```bash
export DISPATCH_PROVIDER=openrouter    # or: siliconflow
~/.claude/skills/giasip-dispatch/scripts/api-dispatch.sh --model deepseek "Hello"
```

- Get a key: OpenRouter → <https://openrouter.ai/keys> · SiliconFlow → <https://siliconflow.cn>
- Provider resolution: `--via <provider>` flag > `$DISPATCH_PROVIDER` env > `direct`. Escape hatch for any model the alias table misses: `--model-id <raw>` (e.g. `--via openrouter --model-id anthropic/claude-3.7-sonnet`).
- **Caveats:** OpenRouter passes model inference pricing through at parity (no per-token markup) but takes ~5.5% on credit top-ups, and needs a VPN in mainland China. SiliconFlow is China-direct but open-source/domestic only (no Claude/GPT/Gemini); some models rate-limit unverified accounts (e.g. ~100 requests/day on certain DeepSeek tiers) — check its current Rate Limits. Intl users route SiliconFlow via `export SILICONFLOW_BASE_URL=https://api.siliconflow.com/v1`.
- Aggregator model IDs go stale fast — the alias → model-ID maps live in `references/model-roster.md`; if a call 404s, verify on the vendor's models page or pass `--model-id`.

### 2. Advanced — per-vendor direct keys

If you already hold per-vendor keys (or want to avoid the aggregator's credit-top-up fee), call each vendor directly. This needs a **separate** `.env` **per vendor** in `~/.config/ai-keys/`:

| Model | File | Content |
|-------|------|---------|
| DeepSeek | `deepseek.env` | `export DEEPSEEK_API_KEY=...` |
| Qwen (Tongyi) | `dashscope.env` | `export DASHSCOPE_API_KEY=...` |
| GLM (Zhipu) | `zai.env` | `export ZAI_API_KEY=...` |
| Doubao (Volcengine) | `volcengine.env` | `export ARK_API_KEY=...` |
| MiniMax | `minimax.env` | `export MINIMAX_API_KEY=...` |

Test (adjust the path to your install location — e.g. a global install): `~/.claude/skills/giasip-dispatch/scripts/api-dispatch.sh --model deepseek "Hello"`

> Specific model names (e.g., `deepseek-v4-pro`) are defined in the `case` branches of `api-dispatch.sh` and may change as vendors release new versions — update `MODEL_ID` in the script if a call fails. See `references/model-roster.md` for the current roster.

### 3. CLI invocation — agentic tasks (requires local install + login)

The aggregator/API paths cover pure analysis and multi-dispatch. CLI channels are for **agentic** work a chat API can't do — Codex write-mode (edits files), Gemini native PDF/image vision, Kimi's coding harness.

| Model | Install | Auth |
|-------|---------|------|
| Codex | `npm i -g @openai/codex` | ChatGPT account |
| Gemini | `npm i -g @google/gemini-cli` | Google account |
| Kimi | `uv tool install kimi-cli` (or API key only) | kimi.com / Moonshot key |

Dependency check: `command -v codex gemini kimi node curl python3 jq perl`

> **Kimi has two backends.** The default `kimi-dispatch.sh` calls the **Moonshot API** directly (it's really an API channel, not CLI) — needs `~/.config/ai-keys/kimi-moonshot.env` containing `MOONSHOT_API_KEY`, no `kimi` CLI required. Adding `KIMI_FOR_CODING=1` switches to the **Kimi CLI** coding endpoint — that path needs the `kimi` CLI installed *plus* `~/.config/ai-keys/kimi.env` containing `KIMI_API_KEY`.
>
> **`perl` is required** by the Gemini and Kimi wrappers for portable timeout control — preinstalled on macOS, but install it on minimal Linux images.

> All scripts read keys via `source ~/.config/ai-keys/*.env` — **your keys stay local and are never in this repo**.

---

## What's Included

| File | Description |
|------|-------------|
| `docs/claim-ledger-method.md` | The Claim Ledger Method — full write-up of the evidence-grounding approach (and its own claims audited by it) |
| `examples/README.md` | Worked example — how a confirmed, a quarantined, and a bounced claim flow through the gates |
| `skills/giasip-research/references/platform-profiles.md` | Deep Research platform capability cards (speed/quality/context ratings) |
| `skills/giasip-research/references/matching-rules.md` | Platform matching decision tree (language routing, special requirements) |
| `skills/giasip-research/references/fact-check-protocol.md` | Independent fact-check protocol with cross-faction discipline |
| `skills/giasip-research/agents/openai.yaml` | Codex UI metadata, default `$giasip-research` prompt, and implicit invocation policy |
| `skills/giasip-research/references/subagent-templates.md` | Cross-runtime recon worker templates with ClaimCard schema |
| `plugins/giasip/.codex-plugin/plugin.json` | Codex Plugin manifest and `giasip` component namespace |
| `.agents/plugins/marketplace.json` | Git/repo marketplace entry used by `codex plugin marketplace add` |
| `scripts/sync_codex_plugin.py` | Builds/checks both generated Research targets from the neutral canonical checkout |
| `docs/CODEX-PLUGIN.md` | Plugin architecture, installation, update, and validation guide |
| `skills/giasip-dispatch/references/model-roster.md` | Model roster with per-model strengths and multi-dispatch lineups |
| `skills/giasip-dispatch/scripts/dispatch-persist.mjs` | Persists dispatch responses to `~/.cache/dispatch/` (call explicitly or hook into dispatch scripts) |
| `skills/giasip-dispatch/scripts/stop-review-gate.mjs` | Claude Code stop hook — advisory Codex code review gate |

## Chinese version

A Chinese reading edition is available under [`locales/zh/`](locales/zh/). The installable directories in this repository are generated release artifacts; the maintained semantic source lives in the neutral `agent-skills/portable/research/` canonical layer and is recorded by source hash in each target.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT © GiaSip
