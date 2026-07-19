# GiaSip Codex Plugin

GiaSip Research has two Codex distribution surfaces backed by one neutral canonical workflow:

| Surface | Install | Invoke |
|---|---|---|
| Standalone Agent Skill | `npx skills add GiaSip/giasip-skills --global --skill giasip-research --agent codex --yes` | `$giasip-research` |
| GiaSip Codex Plugin | `codex plugin add giasip@giasip-skills` | `$giasip:research` |

## Architecture

- `agent-skills/portable/research/` in the neutral agent-system checkout is the only
  hand-edited behavioral source of truth.
- `skills/giasip-research/` is a generated standalone target that preserves backward
  compatibility for Claude Code and standalone Agent Skills installs.
- `plugins/giasip/.codex-plugin/plugin.json` defines the stable `giasip` component namespace.
- `plugins/giasip/skills/research/` is a separately generated Codex-native target; it
  contains only the Codex runtime contract and uses the `$giasip:research` namespace.
- Both targets carry `BUILD-PROVENANCE.json` with identical canonical source hashes
  and semantic invariants.
- `.agents/plugins/marketplace.json` exposes the Plugin from this Git repository.
- `giasip-dispatch` is **not bundled** because it remains Claude Code-native.

This keeps `$giasip-research` backward-compatible for standalone users while providing the shorter, extensible `$giasip:research` Plugin namespace.

## Install

```bash
codex plugin marketplace add GiaSip/giasip-skills
codex plugin add giasip@giasip-skills
```

After installation, start a new Codex task and invoke `$giasip:research`.

## Maintain the generated bundle

After changing the neutral canonical Research method, regenerate and verify both targets:

```bash
python3 scripts/sync_codex_plugin.py --canonical-root ~/Projects/active/agent-system
python3 scripts/sync_codex_plugin.py --canonical-root ~/Projects/active/agent-system --check
```

Never edit either generated Research directory directly. Without the canonical checkout,
`--check` still verifies that both checked-in targets share one provenance and identical
references; with `--canonical-root`, it also performs a byte-for-byte rebuild check.

## Validate locally

```bash
python3 -m unittest tests/test_giasip_research_portability.py -v
uv run --with pyyaml python \
  ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/giasip
```

For a clean install test, add this repository as a local marketplace in an isolated Codex home, install `giasip@giasip-skills`, and confirm that the installed plugin contains only `skills/research/`.

## Official references

- [Build plugins](https://learn.chatgpt.com/docs/build-plugins)
- [Build skills](https://learn.chatgpt.com/docs/build-skills)
