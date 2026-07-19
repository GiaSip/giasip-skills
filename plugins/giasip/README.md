# GiaSip Research Codex Plugin

This directory is the Codex Plugin distribution package for GiaSip Research.

- Plugin namespace: `giasip`
- Bundled skill: `research`
- Invocation: `$giasip:research`
- Canonical source: neutral `agent-skills/portable/research/` (recorded in `BUILD-PROVENANCE.json`)

The `skills/research/` directory is generated. Do not edit it directly; reconcile
the neutral canonical source and run the following from the repository root:

```bash
python3 scripts/sync_codex_plugin.py --canonical-root <agent-system-checkout>
```
