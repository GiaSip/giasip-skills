# GiaSip Research 中文阅读说明

> 本目录不是第二份可安装 Skill，也不单独维护执行逻辑。

`giasip-research` 的唯一行为真源位于仓库根目录的 [`skills/giasip-research/SKILL.md`](../../../../skills/giasip-research/SKILL.md)。该文件同时定义：

- 共享的广度优先 Quick Recon、Claim Ledger、Deep Research 升级和 Mini Assurance 流程；
- 论证/决策题（Adjudication）的**假设脊椎**（论证效度第三轴：广度后立竞争假设（含 null）→ 证伪式 Round 2 → warrant-gated / underdetermined 结论；检索/Mapping 题按设计跳过，防僵硬），详见 [`references/hypothesis-spine.md`](../../../../skills/giasip-research/references/hypothesis-spine.md)；
- Claude Code 的 `WebSearch` / `WebFetch` / SubAgent 映射；
- Codex 的 web 工具 / `spawn_agent` 映射；
- worker 或 reviewer 并发槽不可用时的显式降级路径。

安装与触发：

- Claude Code：`/giasip-research`
- Codex：`$giasip-research`
- 两者均保留 `giasip-research` 这一 GiaSip 品牌名。

中文用户可以直接用中文提出调研需求；主 Skill 的 `description` 已声明支持 Chinese，不需要再安装一份中文 `SKILL.md`。
