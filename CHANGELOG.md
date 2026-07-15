# Changelog

All notable changes to this project will be documented in this file.

## [1.4.0] — 2026-07-15

### Added
- **GiaSip Codex Plugin**: added a validated `.codex-plugin/plugin.json` package with the `giasip` namespace and `$giasip:research` invocation.
- **Repo marketplace**: added `.agents/plugins/marketplace.json` so Codex can install the Plugin from `GiaSip/giasip-skills`.
- **Generated-bundle sync guard**: added `scripts/sync_codex_plugin.py` and regression coverage to keep the Plugin copy derived from the canonical `giasip-research` skill.
- **Codex Plugin guide**: documented standalone versus Plugin installation, namespacing, maintenance, and validation in `docs/CODEX-PLUGIN.md`.

### Changed
- README (English/Chinese) now distinguishes standalone `$giasip-research` from Plugin `$giasip:research` installation.
- Distribution manifests are versioned at `1.4.0`.
- The Codex Plugin intentionally excludes `giasip-dispatch` until that Claude Code-native workflow receives its own Codex adaptation.

## [1.3.0] — 2026-07-15

### Added
- **giasip-research cross-runtime adapter**: one shared research method now maps explicitly to Claude Code (`WebSearch` / `WebFetch` / SubAgents) and Codex (available web tools / `spawn_agent`), with a documented sequential fallback when worker concurrency is unavailable.
- **Codex distribution metadata**: added `agents/openai.yaml` with the GiaSip Research display name, `$giasip-research` default prompt, and implicit-invocation policy.
- **giasip-research Step 0 — run directory + manifest persistence**: Recon/DR runs now persist artifacts, ledger, and a `manifest.md` state anchor to a run directory — enabling Mini Assurance to read raw artifacts and cross-session recovery (user returns days later with DR results).
- **giasip-research Step 6 — Deep Research result reflow**: DR reports now flow back through the Claim Ledger Gate + reconciliation + persistence, closing the previously unguarded escalation / skip-Recon half of tasks.

### Fixed
- **giasip-research hallucination-tolerance enum**: added the missing "extremely low" tier — the fact-check protocol's `extremely low + academic-grade` trigger could never fire against the old `low/medium/high` enum, silently disabling it.
- **giasip-research Layer 1 naming**: unified Perplexity "Pro Search" vs "Deep Research" (three conflicting mentions) to Deep Research, matching the default-DR discipline.
- **dispatch script paths**: replaced the non-existent `${CLAUDE_SKILL_DIR}` env var — Claude Code does not inject it, so it resolved to an empty path and broke every `dispatch` script call on a fresh install — with a `BASE_DIR` shell variable the agent sets once at the start of a session.
- README (en/zh) no longer claims script paths "resolve automatically"; the wording now matches the `BASE_DIR` convention in SKILL.md.

### Changed
- **giasip-research portable skill contract**: standardized installable frontmatter to `name` + trigger-focused `description`, replaced Claude-only execution language with host-neutral worker/web terminology, and documented Claude Code and Codex installation/invocation without renaming the `giasip-research` brand.
- **Mini Assurance portability**: when a fresh reviewer slot is unavailable, the workflow now tries an idle independent worker and finally a clearly labeled non-independent artifact audit instead of silently skipping assurance.
- **Chinese locale drift control**: replaced the stale second Chinese `SKILL.md` with a non-installable reading guide; the root `skills/giasip-research/` directory is the single installable behavioral source of truth.
- **Distribution version sync**: bumped the Claude Code plugin and marketplace manifests to `1.3.0` alongside the cross-runtime Research release.
- **giasip-research unified paid-quota authorization**: any external paid action (DR escalation, paid fact-check, cross-faction reviewer) now reports platform + estimated count/cost and waits for user confirmation before running; removed the contradictory "only pause when escalating DR" clause.
- **giasip-research claim_id + Template B**: claim_id is now globally unique (`<run_id>-<facet>-<seq>`) to avoid collisions across facets / Round 2 / DR reflow; Template B now includes only `confirmed` claims + a no-Recon variant + a mandatory authorization block.
- README (en/zh): documented Kimi's two backends — default `kimi-dispatch.sh` calls the Moonshot API (`kimi-moonshot.env` / `MOONSHOT_API_KEY`, no CLI) vs `KIMI_FOR_CODING=1` Kimi CLI endpoint (`kimi.env` / `KIMI_API_KEY`); added `perl` to the dependency list.
- Removed the non-standard `compatibility` frontmatter field; `giasip-research` now carries explicit Claude Code and Codex runtime mappings, while `giasip-dispatch` remains Claude Code-native.
- `.gitignore`: ignore `*.env` / `node_modules` / logs / `tmp/` to prevent committing API keys.

## [1.2.0] — 2026-06-13

### Changed
- Restructured both skills to standard SKILL.md distribution format (agentskills.io spec)
- Moved supporting docs into `references/` subdirectories
- Slimmed `giasip-research/SKILL.md` from 424 to 276 lines by extracting protocols to references/
- Enhanced SKILL.md frontmatter with `version`, `author`, `license`, `compatibility` fields
- Updated dispatch model roster to current versions (DeepSeek V4-Pro / Qwen3.6 Plus / GLM-5.1 / Kimi K2.6 / Doubao Seed-2.0 Pro / MiniMax M2.7)

### Added
- `skills/giasip-dispatch/scripts/dispatch-persist.mjs` — response logging sink
- `skills/giasip-dispatch/scripts/stop-review-gate.mjs` — Codex stop-hook for code review gating
- `skills/giasip-dispatch/references/model-roster.md` — full model roster with per-model strengths and multi-dispatch lineup recommendations
- `skills/giasip-research/references/fact-check-protocol.md` — extracted fact-check protocol (v2.2+v2.4) + Mini Assurance audit
- `skills/giasip-research/references/subagent-templates.md` — extracted SubAgent instruction templates (Round 1 + Round 2) + unit sanity check
- Complexity routing section in dispatch (auto-selects strategy based on task nature)
- Kimi thinking model discipline (timeout, fast mode, SSE streaming)
- Response logging with `DISPATCH_BATCH_ID` grouping for multi-dispatch runs

## [1.1.0] — 2026-06-08

### Changed
- Adopted `giasip-*` name prefix convention for both skills
- Added `npx skills add` as primary installation method
- Renamed repo to `giasip-skills` for brand consistency
- Restructured as Claude Code plugin with `.claude-plugin/` manifest

## [1.0.0] — 2026-05-04

### Added
- Initial release: `giasip-research` (research orchestrator) and `giasip-dispatch` (multi-model dispatcher)
- 4 dispatch scripts: `api-dispatch.sh`, `codex-appserver.mjs`, `gemini-supervisor.sh`, `kimi-dispatch.sh`
- Research supporting docs: `matching-rules.md`, `platform-profiles.md`
- Chinese locale support (`locales/zh/`)
