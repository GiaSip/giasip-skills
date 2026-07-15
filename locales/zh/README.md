# giasip-skills

> ✦ GiaSip 的跨运行时 Agent 技能集 · github.com/GiaSip
>
> *`giasip-research` 共用一套调研方法，内置 Claude Code 和 Codex 两层薄适配；既可独立安装，也可通过 `giasip` Codex Plugin 获得 namespace。`giasip-dispatch` 仍是 Claude Code 原生技能。*

| 技能 | 说明 |
|------|------|
| **giasip-research** | 跨运行时研究调度 — 先用当前 host 的 worker 和网页工具做广度优先 Quick Recon，再决定是否升级到外部 Deep Research。内置两轮 Recon、Claim Ledger、持久化和独立 fact-check。 |
| **giasip-dispatch** | 多模型调用器 — 把任务或 prompt 一键派发给其他 AI 模型（Codex / Gemini / Kimi / DeepSeek / 豆包 / Qwen / GLM / MiniMax）执行并取回结果。纯调用器形态，不内置选型偏好（选哪个模型、单派多派交给你自己的 Claude 临场判断）。 |

## 安装

Codex 有两种分发方式，通常二选一即可。

### 方式一：`npx skills add`（推荐）

```bash
# Claude Code：安装全部技能
npx skills add GiaSip/giasip-skills --global --skill '*' --agent claude-code --yes

# Claude Code：只安装 Research
npx skills add GiaSip/giasip-skills --global --skill giasip-research --agent claude-code --yes

# Codex：只安装 Research
npx skills add GiaSip/giasip-skills --global --skill giasip-research --agent codex --yes

# 先看看仓库里有哪些技能
npx skills add GiaSip/giasip-skills -l
```

### 方式二：Codex Plugin（带 GiaSip namespace）

```bash
codex plugin marketplace add GiaSip/giasip-skills
codex plugin add giasip@giasip-skills
```

Plugin 中用 `$giasip:research`。它只打包已经 Codex 化的 Research，不会把仍属 Claude Code 原生的 `giasip-dispatch` 一起安装。架构与同步方法见 [`docs/CODEX-PLUGIN.md`](../../docs/CODEX-PLUGIN.md)。

### 方式三：作为 Claude Code plugin（仅 Claude Code）

```
/plugin marketplace add GiaSip/giasip-skills
/plugin install giasip-skills@giasip-skills
```

### 方式四：git clone

```bash
git clone https://github.com/GiaSip/giasip-skills
# Claude Code
cp -R giasip-skills/skills/giasip-research ~/.claude/skills/giasip-research
cp -R giasip-skills/skills/giasip-dispatch ~/.claude/skills/giasip-dispatch

# Codex / 兼容 Agent Skills 的 host
cp -R giasip-skills/skills/giasip-research ~/.agents/skills/giasip-research
```

> Claude Code 中用 `/giasip-research`，Codex 中用 `$giasip-research`；两者也可按自然语言调研意图自动触发。`giasip-dispatch` 仍只在 Claude Code 中用 `/giasip-dispatch`。

---

## giasip-research — 依赖

**基本零外部依赖，开箱即用**——Claude Code 映射到 WebSearch / WebFetch / SubAgent，Codex 映射到当前可用的 web 工具 / `spawn_agent`。如果并发 worker 不可用，会明确改为顺序执行同一批切面，而不是静默减少覆盖面。

> 本目录是中文阅读版；可安装的行为唯一真源是仓库根目录下的 `skills/giasip-research/`，以避免中英两份执行逻辑漂移。

唯一需配置：`skills/giasip-research/references/platform-profiles.md` 里有一张「平台可用性」表，按你实际订阅的 Deep Research 平台（ChatGPT / Gemini / Perplexity / Kimi 等）填 ✅/❌，匹配逻辑会据此跳过未订阅的平台。模型阵容见 `skills/giasip-dispatch/references/model-roster.md`。

## giasip-dispatch — 依赖

两类调用通道，按需配置：

### 1. API 直调（只需 API key，最快）

支持 DeepSeek / Qwen / GLM / 豆包 / MiniMax。在 `~/.config/ai-keys/` 放对应 `.env` 文件：

| 模型 | 文件 | 内容 |
|------|------|------|
| DeepSeek | `deepseek.env` | `export DEEPSEEK_API_KEY=...` |
| Qwen（通义） | `dashscope.env` | `export DASHSCOPE_API_KEY=...` |
| GLM（智谱） | `zai.env` | `export ZAI_API_KEY=...` |
| 豆包（火山引擎） | `volcengine.env` | `export ARK_API_KEY=...` |
| MiniMax | `minimax.env` | `export MINIMAX_API_KEY=...` |

测试（按你的安装位置调整路径——全局安装为例）：`~/.claude/skills/giasip-dispatch/scripts/api-dispatch.sh --model deepseek "你好"`

> 具体模型名（如 `deepseek-v4-pro`）写在 `api-dispatch.sh` 的 `case` 分支里，会随厂商版本更新——跑不通时去脚本里改 `MODEL_ID`。

### 2. CLI 调用（需本地装并登录对应 CLI）

| 模型 | 安装 | 登录 |
|------|------|------|
| Codex | `npm i -g @openai/codex` | ChatGPT 账号 |
| Gemini | `npm i -g @google/gemini-cli` | Google 账号 |
| Kimi | `uv tool install kimi-cli`（或仅用 API key） | kimi.com / Moonshot key |

依赖检查：`command -v codex gemini kimi node curl python3 jq perl`

> **Kimi 有两个后端。** 默认的 `kimi-dispatch.sh` 直接调 **Moonshot API**（其实是 API 通道，不是 CLI）——需要 `~/.config/ai-keys/kimi-moonshot.env`（含 `MOONSHOT_API_KEY`），不需要装 `kimi` CLI。加 `KIMI_FOR_CODING=1` 才切到 **Kimi CLI** coding endpoint——这条路径需要装 `kimi` CLI **外加** `~/.config/ai-keys/kimi.env`（含 `KIMI_API_KEY`）。
>
> **`perl` 是必需的**：Gemini 和 Kimi wrapper 用它做可移植超时控制——macOS 自带，精简 Linux 镜像需自行安装。

> 所有脚本通过 `source ~/.config/ai-keys/*.env` 读取 key，**密钥只在你本地，不在本仓库**。

---

## License

MIT © GiaSip
