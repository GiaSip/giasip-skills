#!/usr/bin/env python3
"""Build or verify generated GiaSip Research targets from the neutral canonical source."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANONICAL_ROOT = Path(
    os.environ.get(
        "AGENT_SYSTEM_ROOT",
        "~/Projects/active/agent-system",
    )
).expanduser()
CLAUDE_TARGET = REPO_ROOT / "skills" / "giasip-research"
CODEX_PLUGIN = REPO_ROOT / "plugins" / "giasip"


def release_version() -> str:
    manifest = json.loads(
        (REPO_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    return str(manifest["version"])


def builder(root: Path) -> Path:
    path = root / "scripts" / "build-research-codex-target.py"
    if not path.is_file():
        raise SystemExit(
            "neutral Research builder not found. Pass --canonical-root pointing to "
            "the agent-system checkout; public target directories are generated artifacts."
        )
    return path


def run_builder(root: Path, profile: str, destination: Path, check: bool) -> None:
    command = [
        sys.executable,
        str(builder(root)),
        "--root",
        str(root),
        "--profile",
        profile,
        "--plugin-version",
        release_version(),
    ]
    if profile in {"claude", "standalone"}:
        command.extend(["--output-skill", str(destination)])
    else:
        command.extend(["--output-plugin", str(destination)])
    if check:
        command.append("--check")
    subprocess.run(command, cwd=root, check=True)


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def internal_check() -> None:
    """Verify checked-in targets agree without requiring the private source checkout."""
    claude_provenance = load_json(CLAUDE_TARGET / "BUILD-PROVENANCE.json")
    codex_provenance = load_json(CODEX_PLUGIN / "BUILD-PROVENANCE.json")
    if claude_provenance.get("profile") != "standalone":
        raise SystemExit("standalone target provenance must declare profile=standalone")
    if codex_provenance.get("profile") != "codex":
        raise SystemExit("Codex plugin provenance must declare profile=codex")
    for key in ("source_root", "source_hashes", "semantic_contract"):
        if claude_provenance.get(key) != codex_provenance.get(key):
            raise SystemExit(f"generated target provenance disagrees on {key}")

    claude_skill = (CLAUDE_TARGET / "SKILL.md").read_text(encoding="utf-8")
    codex_skill = (
        CODEX_PLUGIN / "skills" / "research" / "SKILL.md"
    ).read_text(encoding="utf-8")
    required = [
        ("Claude Code Runtime Contract", claude_skill),
        ("$giasip-research", (CLAUDE_TARGET / "agents" / "openai.yaml").read_text(encoding="utf-8")),
        ("Codex Runtime Contract", codex_skill),
        ("$giasip:research", (CODEX_PLUGIN / "skills" / "research" / "agents" / "openai.yaml").read_text(encoding="utf-8")),
    ]
    for token, text in required:
        if token not in text:
            raise SystemExit(f"generated target missing {token!r}")
    if "Codex Standalone Runtime Contract" not in claude_skill:
        raise SystemExit("standalone target lacks its Codex compatibility contract")
    if "Claude Code Runtime Contract" in codex_skill:
        raise SystemExit("Codex target contains the Claude runtime contract")

    claude_refs = sorted(
        path.relative_to(CLAUDE_TARGET / "references")
        for path in (CLAUDE_TARGET / "references").rglob("*")
        if path.is_file()
    )
    codex_ref_root = CODEX_PLUGIN / "skills" / "research" / "references"
    codex_refs = sorted(
        path.relative_to(codex_ref_root)
        for path in codex_ref_root.rglob("*")
        if path.is_file()
    )
    if claude_refs != codex_refs:
        raise SystemExit("Claude and Codex generated reference file lists differ")
    for relative in claude_refs:
        if (
            CLAUDE_TARGET / "references" / relative
        ).read_bytes() != (codex_ref_root / relative).read_bytes():
            raise SystemExit(f"generated reference differs: {relative}")

    plugin = load_json(CODEX_PLUGIN / ".codex-plugin" / "plugin.json")
    if plugin.get("name") != "giasip" or plugin.get("version") != release_version():
        raise SystemExit("Codex Plugin name/version is not synchronized")
    print("Generated GiaSip Research targets are internally consistent.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--canonical-root",
        type=Path,
        help="agent-system checkout containing the neutral Research source and builder",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify checked-in generated targets without changing them",
    )
    args = parser.parse_args()
    root = (args.canonical_root or DEFAULT_CANONICAL_ROOT).expanduser().resolve()

    if args.check:
        internal_check()
        if (root / "scripts" / "build-research-codex-target.py").is_file():
            run_builder(root, "standalone", CLAUDE_TARGET, check=True)
            run_builder(root, "codex", CODEX_PLUGIN, check=True)
        else:
            print("Canonical checkout unavailable; skipped source-hash rebuild check.")
        return 0

    run_builder(root, "standalone", CLAUDE_TARGET, check=False)
    run_builder(root, "codex", CODEX_PLUGIN, check=False)
    internal_check()
    print(f"Synced neutral Research source -> {CLAUDE_TARGET} and {CODEX_PLUGIN}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
