# Model Roster

> Model names and versions evolve with vendor updates. Check vendor docs before calling.

## Aggregator (★ easy path) — alias → model-ID maps

One aggregator key covers every model below. Set `DISPATCH_PROVIDER=openrouter` (overseas) or `siliconflow` (China), then call `api-dispatch.sh --model <alias>`.

> ⚠️ **These model IDs are the most perishable thing in this repo.** Aggregators rename/retire models constantly. If a call 404s on the model, look it up on the vendor's models page and either update the alias in `scripts/api-dispatch.sh` or pass the correct ID via `--model-id <raw>` (which bypasses this table entirely). Do NOT trust these strings as current without checking.

### OpenRouter (overseas) — `https://openrouter.ai/api/v1` · [models page](https://openrouter.ai/models)

Each alias points at a **sensible current model** per vendor (every alias below live-tested against OpenRouter on 2026-07-19 — each returned HTTP 200). These are defaults for convenience, **not a promise of the absolute top SKU**; to pin an exact tier use `--model-id`.

| Alias | Model ID | Note |
|-------|----------|------|
| `deepseek` | `deepseek/deepseek-v3.2` | reasoner: `deepseek/deepseek-r1` (alias `deepseek-r1`) |
| `qwen` | `qwen/qwen3.6-plus` | Tongyi |
| `glm` | `z-ai/glm-5.2` | Zhipu |
| `kimi` | `moonshotai/kimi-k3` | Moonshot |
| `minimax` | `minimax/minimax-m3` | |
| `claude` | `anthropic/claude-sonnet-5` | bonus — not reachable via the China aggregator |
| `gpt` | `openai/gpt-5.5` | bonus |
| `gemini` | `google/gemini-3.7-flash` | bonus — also handles vision via API. Flash, not Pro: see note below |

### SiliconFlow 硅基流动 (China) — `https://api.siliconflow.cn/v1` · [models page](https://siliconflow.cn/models)

IDs below were **live-tested** against SiliconFlow on 2026-07-19 (each returned HTTP 200). Note SiliconFlow's `Pro/` prefix on some models — the bare form 404s.

| Alias | Model ID | Note |
|-------|----------|------|
| `deepseek` | `deepseek-ai/DeepSeek-V4-Pro` | reasoner: `deepseek-ai/DeepSeek-R1` (alias `deepseek-r1`) |
| `qwen` | `Qwen/Qwen3.6-35B-A3B` | bigger option: `Qwen/Qwen3.5-397B-A17B` |
| `glm` | `zai-org/GLM-5.2` | |
| `kimi` | `Pro/moonshotai/Kimi-K2.6` | needs the `Pro/` prefix; SiliconFlow's latest general Kimi (K3 not hosted here yet — the CLI/Moonshot path uses K3) |
| `minimax` | `MiniMaxAI/MiniMax-M2.5` | |

> China direct-access, no VPN. Open-source / domestic models only — no Claude / GPT / Gemini. Some models rate-limit unverified accounts (e.g. ~100 requests/day on certain DeepSeek tiers) — ID-verify to lift it, and check SiliconFlow's current Rate Limits. Intl users route via `https://api.siliconflow.com/v1` (set `SILICONFLOW_BASE_URL`).

## API Direct Call Models (per-vendor, advanced)

| Parameter | Model | Key File | Context | API Endpoint | Best For |
|-----------|-------|----------|---------|-------------|----------|
| `deepseek` | DeepSeek V4-Pro (thinking mode on) | `deepseek.env` | 1M | api.deepseek.com | Causal chain reasoning, numerical verification, hypothesis testing |
| `qwen` | Qwen3.6 Plus (Tongyi) | `dashscope.env` | 1M | dashscope.aliyuncs.com (compat mode) | Information synthesis, long document processing, structured output |
| `glm` | GLM-5.2 (Zhipu flagship) | `zai.env` | 200K | open.bigmodel.cn | Fact-checking, low hallucination rate, claim verification |
| `doubao` | Doubao Seed-2.0 Pro (ByteDance) | `volcengine.env` | 256K | ark.cn-beijing.volces.com | Chinese expression, writing quality |
| `minimax` | MiniMax M3 | `minimax.env` | — | api.minimaxi.com (override via `MINIMAX_BASE_URL`) | Programming tasks, Office document processing |

## CLI Models

| CLI | Model | Best For |
|-----|-------|----------|
| Codex | GPT-5.5 (xhigh reasoning) | Code review, architecture analysis, deep reasoning |
| Gemini | gemini-3.7-flash (1M context) | Vision/PDF parsing, large context tasks, broad knowledge |
| Kimi | K3 (Chinese-native thinking model) | Chinese business analysis, strategic assessment, creative writing |

> **Why Flash and not Pro for Gemini.** Google's Pro tier has not moved since
> `gemini-3.1-pro-preview` and is still labelled preview, while Flash shipped 3.5 → 3.6 → 3.7.
> As of 2026-08, `gemini-3.7-flash` beats 3.1-Pro on Artificial Analysis' intelligence index
> (56.0 vs 47.7) at roughly a third of the blended price, so the usual "Pro beats Flash" prior
> is the wrong way round for this vendor right now. Re-check before assuming it still holds —
> that's the point of the note, not the specific numbers.

## Multi-Dispatch Lineup Recommendations

| Task Type | Lineup | Rationale |
|-----------|--------|-----------|
| Chinese business/strategic analysis | Kimi + DeepSeek + Doubao | Find blind spots + deconstruct logic + Chinese expression |
| Brand creative/slogan/copywriting | Gemini + Doubao + Kimi | Creative divergence + phonetics + review |
| English technical problems | Codex + Gemini + Kimi | GPT reasoning + Google context + diverse perspective |
| Tech selection/architecture design | Codex + Gemini + DeepSeek | Three different technical judgment systems |
| General/mixed problems | Codex + Gemini + Kimi | Top-tier across three platforms, maximize perspective diversity |
| Ultra-long documents (>100 pages) | Any lineup above + Qwen | Add 1M context processing capability |

Selection principle: **cognitive diversity > quantity**. Pick the smartest, most distinctive models — don't pad the roster. Always use each model's highest-tier configuration; control cost by controlling frequency, not by downgrading per-call quality.
