# GiaSip Codex Plugin

GiaSip Research has two Codex distribution surfaces, both maintained by hand from one
source file.

| Surface | Install | Invoke |
|---|---|---|
| Standalone Agent Skill | `npx skills add GiaSip/giasip-skills --global --skill giasip-research --agent codex --yes` | `$giasip-research` |
| GiaSip Codex Plugin | `codex plugin add giasip@giasip-skills` | `$giasip:research` |

## Architecture

- `skills/giasip-research/SKILL.md` at the repository root is the hand-maintained source of truth.
- `plugins/giasip/.codex-plugin/plugin.json` defines the stable `giasip` component namespace.
- `plugins/giasip/skills/research/SKILL.md` is a manually kept copy of the root skill, with only
  the frontmatter `name:` changed to `research` to match the plugin namespace.
- `.agents/plugins/marketplace.json` exposes the Plugin from this Git repository.
- `giasip-dispatch` is **not bundled** because it remains Claude Code-native.

This keeps `$giasip-research` backward-compatible for standalone users while providing the shorter,
extensible `$giasip:research` Plugin namespace.

## Install

```bash
codex plugin marketplace add GiaSip/giasip-skills
codex plugin add giasip@giasip-skills
```

After installation, start a new Codex task and invoke `$giasip:research`.

## Maintain the bundled copy

After changing `skills/giasip-research/SKILL.md`, copy it to
`plugins/giasip/skills/research/SKILL.md` and change only the frontmatter `name:` to `research`.
There is no generator script — the two files are kept in sync by hand.

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
