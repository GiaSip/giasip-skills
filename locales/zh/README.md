# giasip-skills

> ✦ GiaSip 的跨运行时 Agent 技能集 · github.com/GiaSip
>
> **`giasip-research` 让每一条调研发现都先过一本 Claim Ledger** —— 一份可审计的账本，每条 claim 先被记成一张 ClaimCard，带明确的 **confidence 评级**和 **source-family 来源身份标注**（owner / regulator / official / independent / vendor / aggregate / community）。一连串对抗式关卡**把没有证据支撑的 claim 挡在结论之外**，所以它回答的不只是"我找到了什么"，而是"每条 claim 你该信几分"。一套调研方法，适配 Claude Code 和 Codex 两个 host。
>
> 仓库同时提供 **`giasip-dispatch`**，一个把任务派发给 Codex / Gemini / Kimi / DeepSeek / 豆包 / Qwen / GLM / MiniMax 的多模型调用器。

| 技能 | 它给你什么 |
|------|-----------|
| **giasip-research** | 研究调度器，把每条 claim 都锚定到证据。用当前 host 的 worker 和网页工具做广度优先 Quick Recon，每条发现记成一张 **ClaimCard**（confidence + source family + "原文说的 vs 我推断的"），再过一道 **Claim Ledger Gate** 把无凭据的 claim 挡在结论外；只在任务真需要时才升级到付费 Deep Research —— 花钱前先问，返回的结果还要**重新过账**而非盲信。每次运行落盘，长任务可跨会话续上。独立 fact-check 协议 + fresh-reviewer 审计（direct-delivery 调研默认开）守住诚实。 |
| **giasip-dispatch** | 多模型调用器 —— 把任务或 prompt 一键派发给其他 AI 模型（Codex / Gemini / Kimi / DeepSeek / 豆包 / Qwen / GLM / MiniMax）执行并取回结果。含复杂度路由指引（API vs CLI vs SubAgent、单派 vs 多派），但最终选哪个模型交给你自己的 agent 临场判断。 |

---

## 为什么 giasip-research 与众不同

AI 调研稀缺的从来不是检索广度——谁都能搜。稀缺的是**知道每条 claim 该信几分**。这正是这个 skill 的立身之本。

> _对比对象是常见的"搜索+总结"型**技能**，不是 Deep Research 平台——后者 giasip-research 是**调度**它们，而非与之竞争。_

| | 普通 research 技能 | **giasip-research** |
|---|---|---|
| **每条事实靠什么支撑** | 无——事实融进散文 | 每条记成 ClaimCard（confidence + source family），过 Claim Ledger 审计 |
| **溯源** | "我找到了一些来源" | 每条 claim 标 `owner` / `regulator` / `official` / `independent` / `vendor` / `aggregate` / `community` |
| **无凭据 claim** | 直接混进总结 | 打回，或标 `weak` 隔离出结论句 |
| **验证顺序** | 信模型 | 一手源接地 **>** 来源家族收敛 **>** 跨模型交叉核 |
| **同阵营偏见** | 不设防 | 涉及模型自家阵营时，跨阵营 fact-check |

你拿到的仍是一份可读的报告——ClaimCard 和 Claim Ledger 是报告**背后**的审计线，不是丢到你桌上的东西。

### 一条 claim 长什么样

不是散文里一句没出处的话，每条事实变成一张结构化、可审计的卡片：

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

**Claim Ledger Gate** 随后强制一条你的结论所依赖的规则：一条 `central` claim 若**没有一手源 locator，会被打回重搜一轮**；只有 aggregator 或 vendor 自报支撑的 claim 标 `weak` 移入"待验证"清单——不能出现在结论句里。

### 多数 agent 搞反的验证顺序

跨模型交叉核被广泛当成金标准。giasip-research 把它排在**最后**：

> **一手源接地  >  来源家族收敛  >  跨模型交叉核**

一个真读过一手源的模型，胜过三个凭记忆互相印证的模型。异构 reviewer 是补盲点——不能替代没人读过的一手源。当话题涉及 reviewer 自家阵营时，由**跨阵营**模型投下决定票。

→ 完整方法与思想来源：**[The Claim Ledger Method](../../docs/claim-ledger-method.md)**（英文）· 实例：**[worked example](../../examples/)**（英文）

---

## 一本账，贯穿始终

Claim Ledger 不只用在廉价的第一轮——**同一本账管到整条调研供应链**，包括最贵的环节。这才是它叫*调度器（orchestrator）*而非又一个搜索框的原因。

- **先侦察再花钱。** 默认先跑一轮廉价的内部 recon，只有 native 搜索够不到的缺口才动用付费 Deep Research 平台（你也可以在已知需要时直接指向 Deep Research）。无论哪种，它都会报告平台和预计成本、等你确认——除非你已明说"直接提交、不用问"。
- **只用 confirmed claim 喂付费运行。** 升级时，Deep Research 的 prompt 只用 `confirmed` 状态的 ledger claim 构建，`weak` 和 `unresolved` 不进——付费运行不会被没验证的锚点带偏。
- **返回的 Deep Research 重新过账，不盲信。** 拿回来的报告不是直接粘贴。它的 claim 会抽成同样的 ClaimCard、过同一道 gate、与 recon ledger 对账——付费平台一样会幻觉，不因为贵就免检。
- **从上次停下的地方继续。** 一次 Deep Research 可能跑一小时，你常常隔天才回来。每次运行都持久化 ledger、原始 artifact 和一个 `manifest` 状态文件，新会话精确续上上次停的地方。

一句话：**从第一次廉价搜索到最后一份付费报告，claim 是唯一的记账单位。**

> **站在前人工作上。** 有两个动作是刻意借用的：claim 级质控沿用了 Claude Code Workflow 的 deep-research skill，精确的第二轮搜索沿用了 [MiroThinker](https://github.com/MiroMindAI/MiroThinker) 的 Interactive Scaling。giasip-research 在其上加的是账本**经济学**——confirmed-only 播种、重新过账的回流、跨会话持久化——以及来源家族验证顺序。

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

## FAQ

**跟直接让 Claude 做调研有什么区别？**
裸模型不管事实是否有据，都会写出很自信的散文。giasip-research 把"原文说的"和"agent 推断的"分开，给每条 claim 标来源家族，并在结构上拒绝把无凭据的 claim 升格成结论。

**跑起来要花钱吗？**
基本零外部依赖——Quick Recon 用你 host 自带的网页工具。只有任务真需要时（native 搜索够不到的缺口、受限平台/学术源、或高 stakes 的 fact-check）才升级到付费 Deep Research，而且总会先报平台 + 预计成本再问你。

**支持哪些 host 和语言？**
Claude Code 和 Codex，一套调研方法、两层薄适配。中英双语。

**这些关卡是 prompt 规则——模型不能直接无视吗？**
所以最后一道防线不是 prompt。在 direct-delivery 调研里，一个**独立 context 的 fresh reviewer** 会重读**落盘的原始 artifact**（而不是模型自己写的摘要），给每条结论标 `supported` / `unverifiable` / `conflict`。读原始证据而非模型自述，正是抓住"看似合理但没证据"的关键。

**~85–90% 准确率是怎么回事？**
这是来自少量内部案例的**假设**（N 很小）——**不是**公开 benchmark，也**不是**对其他工具的测量：同一条管道，关掉关卡约 ~70–80%，开启后 ~85–90%。诚实的结论不在这个数字，而在于——无凭据的陈述在结构上更难进入你的结论，因为 Claim Ledger Gate 和 fresh-reviewer 审计横在证据与结论之间。

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

> 调用面因安装方式而异：**独立安装**（方式一、四）在 Claude Code 用 `/giasip-research`、Codex 用 `$giasip-research`；**Codex Plugin**（方式二）用 `$giasip:research`；**Claude Code plugin**（方式三）的技能带 plugin namespace——`/giasip-skills:giasip-research` 和 `/giasip-skills:giasip-dispatch`。`giasip-dispatch` 独立安装时在 Claude Code 用 `/giasip-dispatch`。

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

## 更多文档

- [The Claim Ledger Method](../../docs/claim-ledger-method.md)（英文）—— 证据接地方法的完整说明，并用自身方法审计自己的主张。
- [worked example](../../examples/)（英文）—— confirmed / weak / unresolved 三条 claim 走一遍关卡的实例。
- 中文为阅读版；深入文档目前以英文为准。

## License

MIT © GiaSip
