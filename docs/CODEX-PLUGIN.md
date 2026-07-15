# GiaSip Codex Plugin

GiaSip Research has two Codex distribution surfaces backed by one canonical workflow:

| Surface | Install | Invoke |
|---|---|---|
| Standalone Agent Skill | `npx skills add GiaSip/giasip-skills --global --skill giasip-research --agent codex --yes` | `$giasip-research` |
| GiaSip Codex Plugin | `codex plugin add giasip@giasip-skills` | `$giasip:research` |

## Architecture

- `skills/giasip-research/` is the only hand-edited behavioral source of truth.
- `plugins/giasip/.codex-plugin/plugin.json` defines the stable `giasip` component namespace.
- `plugins/giasip/skills/research/` is generated from the canonical skill. Its only intentional transformations are `name: research` and `$giasip:research` invocation metadata.
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

After changing the canonical Research skill, regenerate and verify the Plugin copy:

```bash
python3 scripts/sync_codex_plugin.py
python3 scripts/sync_codex_plugin.py --check
```

Never edit `plugins/giasip/skills/research/` directly. The sync check fails when that generated bundle diverges from `skills/giasip-research/`.

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
