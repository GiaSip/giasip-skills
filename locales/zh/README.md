# giasip-skills

> ✦ GiaSip 的跨运行时 Agent 技能集 · github.com/GiaSip
>
> **`giasip-research` 帮用户拿到回答其问题的准确信息。** 把题目拆成 2–3 个互补切面，并行派子 agent 各查一个切面，每个最多 15 次搜索/抓取；主 agent 综合写一份 `report.md`，附全部发现、来源 URL，末尾单独一节「待核实」。硬规则：每条事实带来源 URL，查不到就写「查不到」而非凭记忆补，禁止 `rm -rf`。2026-09-05/06 两轮对照实验：把这个 skill 从 0 行长到 144 行再到 433 行，精度持平、召回反而收窄、花费 6–13 倍——所以它停在 18 行。核验是独立的一道工序，不属于调研本身。
>
> 仓库同时提供 **`giasip-dispatch`**，一个把任务派发给 Codex / Gemini / Kimi / DeepSeek / 豆包 / Qwen / GLM / MiniMax 的多模型调用器。

| 技能 | 它给你什么 |
|------|-----------|
| **giasip-research** | 把题目拆成 2–3 个互补切面，并行派子 agent 各查一个切面（每个最多 15 次搜索/抓取，只查不下结论），主 agent 再综合写一份 `report.md`——先回答问题，列出全部实体和 URL，正文 ≤200 行，末尾单独一节「待核实」。每条事实带来源 URL；查不到就写「查不到」；对外署名/报价/法规结论前先跑一轮核验。 |
| **giasip-dispatch** | 多模型调用器 —— 把任务或 prompt 一键派发给其他 AI 模型（Codex / Gemini / Kimi / DeepSeek / 豆包 / Qwen / GLM / MiniMax）执行并取回结果。含复杂度路由指引（API vs CLI vs SubAgent、单派 vs 多派），但最终选哪个模型交给你自己的 agent 临场判断。 |

---

## 快速开始

1. **为你的 host 安装 Research**：
   ```bash
   # Claude Code
   npx skills add GiaSip/giasip-skills --global --skill giasip-research --agent claude-code --yes

   # Codex
   npx skills add GiaSip/giasip-skills --global --skill giasip-research --agent codex --yes
   ```

2. **试一下**：
   - Claude Code：`/giasip-research 研究一下人形机器人监管的现状`
   - Codex：`$giasip-research 研究一下人形机器人监管的现状`
   - 或者直接用自然语言描述调研任务，两个 host 都会自动触发。

---

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

Plugin 中用 `$giasip:research`。它只打包 Research，不会把仍属 Claude Code 原生的 `giasip-dispatch` 一起安装。架构说明见 [`docs/CODEX-PLUGIN.md`](../../docs/CODEX-PLUGIN.md)。

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

> 调用面因安装方式而异：**独立安装**（方式一、四）在 Claude Code 用 `/giasip-research`、Codex 用 `$giasip-research`；**Codex Plugin**（方式二）用 `$giasip:research`；**Claude Code plugin**（方式三）的技能带 plugin namespace——`/giasip-skills:giasip-research` 和 `/giasip-skills:giasip-dispatch`。`giasip-dispatch` 独立安装时在 Claude Code 用 `/giasip-dispatch`。

---

## giasip-research — 依赖

**零外部依赖，开箱即用**——用你 host 自带的网页搜索/抓取工具和子 agent（Claude Code 的 WebSearch / WebFetch / SubAgent，或 Codex 的对应能力）。没有需要填写的配置文件。

## giasip-dispatch — 依赖

按需选路径。**大多数人用易用路径——一个聚合平台 key，不必逐厂商注册。**

### 1. 易用路径 —— 一个聚合平台 key（推荐）

一个 key 通过 OpenAI 兼容的聚合平台调多个模型。按地区选一个，在 `~/.config/ai-keys/` 放**一个** `.env`，设一次 provider，之后所选 provider 支持的每个别名都能用。

| 地区 | 平台 | 文件 | 内容 | 覆盖 |
|------|------|------|------|------|
| 海外 | **OpenRouter** | `openrouter.env` | `export OPENROUTER_API_KEY=...` | DeepSeek / Qwen / GLM / Kimi / MiniMax **+ Claude / GPT / Gemini** |
| 国内 | **硅基流动** SiliconFlow | `siliconflow.env` | `export SILICONFLOW_API_KEY=...` | DeepSeek / Qwen / GLM / Kimi / MiniMax |

```bash
export DISPATCH_PROVIDER=openrouter    # 或 siliconflow
~/.claude/skills/giasip-dispatch/scripts/api-dispatch.sh --model deepseek "你好"
```

- 申请 key：OpenRouter → <https://openrouter.ai/keys>；硅基流动 → <https://siliconflow.cn>
- provider 解析优先级：`--via <provider>` 标志 > `$DISPATCH_PROVIDER` env > `direct`。别名表覆盖不到的模型用逃生口 `--model-id <raw>`（如 `--via openrouter --model-id anthropic/claude-3.7-sonnet`）。
- **注意**：OpenRouter 推理价格按原价透传（不加 per-token 加价），但充值 credits 收约 5.5% 手续费、大陆需梯子；硅基流动国内直连但仅国产/开源模型（无 Claude/GPT/Gemini），部分模型对未实名账户有速率限制（如某些 DeepSeek 档约 100 请求/天，以官方 Rate Limits 为准）。国际站用户 `export SILICONFLOW_BASE_URL=https://api.siliconflow.com/v1`。
- 聚合平台的 model ID 极易过时——别名 → model-ID 映射见 `references/model-roster.md`；调用 404 时去 models 页核对或用 `--model-id` 透传。

### 2. 进阶 —— 逐厂商直连 key

已有单厂商 key（或想避开聚合平台的充值手续费）时，直连各厂商。需在 `~/.config/ai-keys/` 放**每个厂商各一个** `.env`：

| 模型 | 文件 | 内容 |
|------|------|------|
| DeepSeek | `deepseek.env` | `export DEEPSEEK_API_KEY=...` |
| Qwen（通义） | `dashscope.env` | `export DASHSCOPE_API_KEY=...` |
| GLM（智谱） | `zai.env` | `export ZAI_API_KEY=...` |
| 豆包（火山引擎） | `volcengine.env` | `export ARK_API_KEY=...` |
| MiniMax | `minimax.env` | `export MINIMAX_API_KEY=...` |

测试（按你的安装位置调整路径——全局安装为例）：`~/.claude/skills/giasip-dispatch/scripts/api-dispatch.sh --model deepseek "你好"`

> 具体模型名（如 `deepseek-v4-pro`）写在 `api-dispatch.sh` 的 `case` 分支里，会随厂商版本更新——跑不通时去脚本里改 `MODEL_ID`。

### 3. CLI 调用 —— agentic 任务（需本地装并登录对应 CLI）

聚合/API 路径覆盖纯分析和多派会诊。CLI 通道用于 chat API 做不到的 **agentic** 工作——Codex 写模式（改文件）、Gemini 原生 PDF/图像视觉、Kimi 的 coding harness。

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

## 更多文档

- [`skills/giasip-research/SKILL.md`](../../skills/giasip-research/SKILL.md)（英文）—— 行为真源。
- [`docs/CODEX-PLUGIN.md`](../../docs/CODEX-PLUGIN.md)（英文）—— Codex Plugin 架构说明。
- 中文为阅读版；深入文档目前以英文为准。

## License

MIT © GiaSip
