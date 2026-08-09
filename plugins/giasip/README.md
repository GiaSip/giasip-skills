# GiaSip Research Codex Plugin

This directory is the Codex Plugin distribution package for GiaSip Research.

- Plugin namespace: `giasip`
- Bundled skill: `research`
- Invocation: `$giasip:research`
- Canonical source: neutral `agent-skills/portable/research/` (recorded in `BUILD-PROVENANCE.json`)

`BUILD-PROVENANCE.json` records paths inside a **separate canonical repository**, not inside
this one — they are provenance metadata, not files you can open here. Everything this skill
needs at runtime ships in this package.

`skills/research/` is generated, including `skills/research/scripts/`, which carries the
Mini Assurance completeness checker so the contract in `references/fact-check-protocol.md`
is enforceable by anyone who downloads this — not just prose. It is stdlib-only Python 3.

Do not edit the generated directory. Reconcile changes into the canonical source, then run
the following from the repository root:

```bash
python3 scripts/sync_codex_plugin.py --canonical-root <path-to-your-canonical-checkout>
```
