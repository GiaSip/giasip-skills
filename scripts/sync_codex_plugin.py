#!/usr/bin/env python3
"""Build or verify the generated Codex plugin copy of GiaSip Research."""

from __future__ import annotations

import argparse
import re
import shutil
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "skills" / "giasip-research"
TARGET = REPO_ROOT / "plugins" / "giasip" / "skills" / "research"
TEXT_SUFFIXES = {".md", ".yaml", ".yml"}


def transform(relative_path: Path, text: str) -> str:
    """Apply only the naming changes required by the plugin namespace."""
    if relative_path == Path("SKILL.md"):
        text, replacements = re.subn(
            r"(?m)^name: giasip-research$",
            "name: research",
            text,
            count=1,
        )
        if replacements != 1:
            raise ValueError("canonical SKILL.md must declare name: giasip-research once")
    return text.replace("$giasip-research", "$giasip:research")


def render(destination: Path) -> None:
    """Render a fresh bundle into a destination that does not yet exist."""
    shutil.copytree(SOURCE, destination)
    for path in sorted(destination.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        relative_path = path.relative_to(destination)
        original = path.read_text(encoding="utf-8")
        rendered = transform(relative_path, original)
        if rendered != original:
            path.write_text(rendered, encoding="utf-8")


def build(destination: Path) -> None:
    """Render first, then replace the previous bundle with rollback on failure."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f".{destination.name}-", dir=destination.parent
    ) as temp_dir:
        staged = Path(temp_dir) / destination.name
        backup = Path(temp_dir) / "previous"
        render(staged)

        if destination.exists():
            destination.rename(backup)
        try:
            staged.rename(destination)
        except BaseException:
            if backup.exists():
                backup.rename(destination)
            raise


def files_under(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file())


def check() -> int:
    with tempfile.TemporaryDirectory(prefix="giasip-codex-plugin-") as temp_dir:
        expected = Path(temp_dir) / "research"
        build(expected)
        expected_files = files_under(expected)
        actual_files = files_under(TARGET)
        if expected_files != actual_files:
            print("Codex plugin bundle is stale: file list differs from canonical skill.")
            return 1
        for relative_path in expected_files:
            if (expected / relative_path).read_bytes() != (TARGET / relative_path).read_bytes():
                print(f"Codex plugin bundle is stale: {relative_path}")
                return 1
    print("Codex plugin bundle is in sync.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync the canonical GiaSip Research skill into the Codex plugin namespace."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify the checked-in plugin bundle without changing it.",
    )
    args = parser.parse_args()
    if args.check:
        return check()
    build(TARGET)
    print(f"Synced {SOURCE} -> {TARGET}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
