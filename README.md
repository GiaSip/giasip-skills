# giasip-skills

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Claude Code](https://img.shields.io/badge/claude--code-compatible-orange)
![Codex](https://img.shields.io/badge/codex-compatible-black)

> **`giasip-research` gets the user accurate answers to their question.** It splits the question into 2–3 complementary facets and runs one sub-agent per facet in parallel, each capped at 15 searches/fetches; the main agent then writes a single `report.md` with every finding, its source URL, and a separate "To verify" section. Hard rules: every fact carries a source URL, "not found" beats a guess from memory, and it never runs `rm -rf`. Two controlled runs (2026-09-05/06) showed growing the skill from 0 to 144 to 433 lines left precision flat, narrowed recall, and cost 6–13× more — so it stays at 18 lines. Verification is a separate pass, not part of research.
>
> The repo also ships **`giasip-dispatch`**, a multi-model dispatcher for routing tasks to Codex / Gemini / Kimi / DeepSeek / Doubao / Qwen / GLM / MiniMax.

| Skill | What it gives you |
|-------|-------------------|
| **giasip-research** | Splits the question into 2–3 complementary facets, runs one sub-agent per facet in parallel (each capped at 15 searches/fetches, gathering only, never concluding), then writes a single `report.md` — answers first, every entity found with its URL, body under 200 lines, closing with a "To verify" section. Every fact carries a source URL; "not found" beats a guess from memory; a verification pass runs before anything ships under a real name, a price, or a legal/financial conclusion. |
| **giasip-dispatch** | A multi-model dispatcher — sends a task or prompt to other AI models (Codex / Gemini / Kimi / DeepSeek / Doubao / Qwen / GLM / MiniMax) and retrieves results. **Start with one aggregator key** (OpenRouter overseas / SiliconFlow in China) instead of signing up per vendor. Includes complexity-routing guidelines (API vs CLI vs SubAgent, single vs multi), but the final model choice is left to your agent's judgment. |

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
skills/giasip-research/                   # Standalone Claude/Codex install target
├── SKILL.md                              # behavioral source of truth
└── FEEDBACK.md                           # point-of-use human feedback log

plugins/giasip/                           # Codex Plugin package
├── .codex-plugin/plugin.json
└── skills/research/SKILL.md              # manually kept copy, name: research

.agents/plugins/marketplace.json          # Repo marketplace for Codex
skills/giasip-dispatch/                   # Claude Code-native dispatcher
```

---

## giasip-research — Dependencies

**Zero external dependencies — works out of the box.** It uses your host's native web search / fetch tools and sub-agents (Claude Code's `WebSearch` / `WebFetch` / SubAgents, or Codex's equivalent). No configuration file to fill in.

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
| `skills/giasip-research/SKILL.md` | The Research skill — behavioral source of truth |
| `skills/giasip-research/FEEDBACK.md` | Append-only point-of-use feedback log; the only input that may change SKILL.md |
| `plugins/giasip/.codex-plugin/plugin.json` | Codex Plugin manifest and `giasip` component namespace |
| `.agents/plugins/marketplace.json` | Git/repo marketplace entry used by `codex plugin marketplace add` |
| `docs/CODEX-PLUGIN.md` | Plugin architecture, installation, and validation guide |
| `skills/giasip-dispatch/references/model-roster.md` | Model roster with per-model strengths and multi-dispatch lineups |
| `skills/giasip-dispatch/scripts/dispatch-persist.mjs` | Persists dispatch responses to `~/.cache/dispatch/` (call explicitly or hook into dispatch scripts) |
| `skills/giasip-dispatch/scripts/stop-review-gate.mjs` | Claude Code stop hook — advisory Codex code review gate |

## Chinese version

A Chinese reading edition is available under [`locales/zh/`](locales/zh/). `skills/giasip-research/SKILL.md` (English) is the behavioral source of truth; `plugins/giasip/skills/research/SKILL.md` is a manually kept copy for the Codex Plugin namespace.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT © GiaSip
