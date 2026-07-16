# giasip-skills

![Version](https://img.shields.io/badge/version-1.4.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Code](https://img.shields.io/badge/claude--code-compatible-orange)
![Codex](https://img.shields.io/badge/codex-compatible-black)

> **`giasip-research` is an evidence-grounded research agent for Claude Code and Codex.**
> Unlike search-and-summarize skills, it treats every fact as a verifiable claim: each one carries an explicit **confidence rating** and a **source-family tag** (owner / regulator / official / independent / vendor / aggregate), and a chain of adversarial gates **rejects unsupported claims before they reach your report**. It answers not just "what did I find," but "how much should you trust each sentence."
>
> The repo also ships **`giasip-dispatch`**, a multi-model dispatcher for routing tasks to Codex / Gemini / Kimi / DeepSeek / Doubao / Qwen / GLM / MiniMax.

| Skill | What it gives you |
|-------|-------------------|
| **giasip-research** | A research orchestrator that grounds every claim in evidence. It runs a breadth-first Quick Recon with your host's native workers and web tools, records each finding as a **ClaimCard** (confidence + source family + "what the source said vs. what I inferred"), passes them through a **Claim Ledger Gate** that bars unsupported claims from your conclusions, and only escalates to a paid Deep Research platform for the gaps native search can't fill. An independent fact-check protocol and a fresh-reviewer audit keep it honest. |
| **giasip-dispatch** | A multi-model dispatcher — sends a task or prompt to other AI models (Codex / Gemini / Kimi / DeepSeek / Doubao / Qwen / GLM / MiniMax) and retrieves results. Includes complexity-routing guidelines (API vs CLI vs SubAgent, single vs multi), but the final model choice is left to your agent's judgment. |

---

## Why giasip-research is different

The scarce thing in AI research isn't retrieval breadth — every agent can search. It's **knowing how much to trust each sentence.** That is what this skill is built around.

| | Generic research skill | **giasip-research** |
|---|---|---|
| **Output unit** | A prose summary | A ledger of claims, each with a confidence rating + source |
| **Provenance** | "I found some sources" | Every claim tagged `owner` / `regulator` / `independent` / `vendor` / `aggregate` |
| **Unsupported claims** | Flow through into the summary | Bounced back, or marked `weak` and quarantined out of conclusion sentences |
| **Verification order** | Trust the model | Primary-source grounding **>** source-family convergence **>** cross-model check |
| **Same-family bias** | Unchecked | Cross-faction fact-check when the topic touches the model's own camp |
| **Accuracy** (internal cases, small N) | ~70–80% baseline | ~85–90% after the Claim Ledger + fresh-reviewer gates |

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
```

The **Claim Ledger Gate** then enforces one rule your conclusions depend on: a `central` claim with **no primary-source locator never reaches your report**, and a claim backed only by aggregators or vendor self-reports is marked `weak` and moved to a "to be verified" list — it cannot appear in a conclusion sentence.

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

**Does it cost money to run?**
Near-zero external dependencies — the Quick Recon uses your host's native web tools. It only escalates to a paid Deep Research platform when it finds a gap native search can't fill, and it reports the platform + expected cost and asks before spending.

**Which hosts and languages does it support?**
Claude Code and Codex, running one shared research method with thin runtime mappings. English and Chinese.

**Is the ~85–90% accuracy figure a guarantee?**
No. It comes from a small number of internal cases (N is small), not a public benchmark. The claim is narrower and more honest: unsupported statements are *structurally harder* to reach your report, because the Claim Ledger Gate and a fresh-reviewer audit sit between the evidence and the conclusion.

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

> Both standalone and Plugin installs use the same Research behavior. The namespace changes only the invocation surface: `$giasip-research` standalone, `$giasip:research` through the Codex Plugin. Claude Code continues to use `/giasip-research`; `giasip-dispatch` remains `/giasip-dispatch` in Claude Code only.

## Distribution Structure

```
skills/giasip-research/                   # Canonical shared Research skill
├── SKILL.md
├── agents/openai.yaml                    # Standalone Codex metadata
└── references/

plugins/giasip/                           # Codex Plugin package
├── .codex-plugin/plugin.json
└── skills/research/                       # Generated namespaced copy

.agents/plugins/marketplace.json          # Repo marketplace for Codex
scripts/sync_codex_plugin.py              # Canonical skill → plugin bundle sync/check
skills/giasip-dispatch/                   # Claude Code-native dispatcher
```

---

## giasip-research — Dependencies

**Near-zero external dependencies — works out of the box.** It maps the same research method onto Claude Code's `WebSearch` / `WebFetch` / SubAgents or Codex's available web tools / `spawn_agent`. If worker concurrency is unavailable, the skill explicitly falls back to sequential facets instead of silently skipping coverage.

The only setup needed: fill in the platform availability table in `skills/giasip-research/references/platform-profiles.md` with your actual Deep Research subscriptions (ChatGPT / Gemini / Perplexity / Kimi, etc.) — the matching logic uses this to skip unsubscribed platforms.

## giasip-dispatch — Dependencies

Two types of dispatch channels; configure what you need:

### 1. API direct call (just needs an API key — fastest)

Supports DeepSeek / Qwen / GLM / Doubao / MiniMax. Place the corresponding `.env` file in `~/.config/ai-keys/`:

| Model | File | Content |
|-------|------|---------|
| DeepSeek | `deepseek.env` | `export DEEPSEEK_API_KEY=...` |
| Qwen (Tongyi) | `dashscope.env` | `export DASHSCOPE_API_KEY=...` |
| GLM (Zhipu) | `zai.env` | `export ZAI_API_KEY=...` |
| Doubao (Volcengine) | `volcengine.env` | `export ARK_API_KEY=...` |
| MiniMax | `minimax.env` | `export MINIMAX_API_KEY=...` |

Test (adjust the path to your install location — e.g. a global install): `~/.claude/skills/giasip-dispatch/scripts/api-dispatch.sh --model deepseek "Hello"`

> Specific model names (e.g., `deepseek-v4-pro`) are defined in the `case` branches of `api-dispatch.sh` and may change as vendors release new versions — update `MODEL_ID` in the script if a call fails. See `references/model-roster.md` for the current roster.

### 2. CLI invocation (requires local install + login)

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
| `skills/giasip-research/references/platform-profiles.md` | Deep Research platform capability cards (speed/quality/context ratings) |
| `skills/giasip-research/references/matching-rules.md` | Platform matching decision tree (language routing, special requirements) |
| `skills/giasip-research/references/fact-check-protocol.md` | Independent fact-check protocol with cross-faction discipline |
| `skills/giasip-research/agents/openai.yaml` | Codex UI metadata, default `$giasip-research` prompt, and implicit invocation policy |
| `skills/giasip-research/references/subagent-templates.md` | Cross-runtime recon worker templates with ClaimCard schema |
| `plugins/giasip/.codex-plugin/plugin.json` | Codex Plugin manifest and `giasip` component namespace |
| `.agents/plugins/marketplace.json` | Git/repo marketplace entry used by `codex plugin marketplace add` |
| `scripts/sync_codex_plugin.py` | Builds or checks the generated `$giasip:research` bundle from the canonical skill |
| `docs/CODEX-PLUGIN.md` | Plugin architecture, installation, update, and validation guide |
| `skills/giasip-dispatch/references/model-roster.md` | Model roster with per-model strengths and multi-dispatch lineups |
| `skills/giasip-dispatch/scripts/dispatch-persist.mjs` | Persists dispatch responses to `~/.cache/dispatch/` (call explicitly or hook into dispatch scripts) |
| `skills/giasip-dispatch/scripts/stop-review-gate.mjs` | Claude Code stop hook — advisory Codex code review gate |

## Chinese version

A Chinese reading edition is available under [`locales/zh/`](locales/zh/). The installable behavioral source of truth remains the root `skills/giasip-research/` directory so the two runtimes cannot drift apart.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT © GiaSip
