#!/usr/bin/env python3
"""Mini Assurance completeness gate — one sentence, one verdict row, checked by a machine.

## Why this exists

The fact-check protocol had long said "for each report topic sentence, assign one of 3
labels" — an instruction with **no mechanically checkable equality behind it**, and nothing
checking it. Observed failure: a reviewer collapsed 27 sentences into 2 range-summary rows
(`| S01-S19 | supported x19 |`) and the gate still printed a pass with exit 0. The same
question audited sentence-by-sentence had caught 1 `unverifiable`; the collapsed run
reported 0. **The audit had silently degraded into a rubber stamp.**

A first-generation gate tried to catch this and had three holes:

  1. the test was `actual < declared`, so **extra rows passed**;
  2. it counted rows without checking IDs, so **`S01` repeated N times counted as N rows**;
  3. worst: **`declared` came out of `audit.md` itself**. A reviewer that collapsed to 2 rows
     and also declared "2 sentences" made `2 < 2` false and **passed**.

So a gate built to stop the audit fooling itself could be bypassed by the audit declaring a
small number. The root cause was handing the authoritative input set to the audited party.
This module externalizes it:

  · the orchestrator writes the topic-sentence list to `audit-input.tsv` **before**
    dispatching the reviewer (that file is the authority);
  · the validator compares the **exact ID set** and never trusts the count declared inside
    `audit.md` (that count is still required — but as something checked, not as the basis
    of the check).

**Any check whose baseline comes from the audited party is decorative.**

## Design boundary (stated honestly)

This validates **structural completeness** only: every input sentence has exactly one verdict
row, and no IDs appear from nowhere. It does **not** validate that the verdicts are correct —
a reviewer can still label everything `supported` and pass. It stops collapse, omission and
fabrication. It does not stop being wrong. Do not advertise it as the latter.

Hosts are expected to run this same file so the rule cannot drift between them.

exit codes: 0 = pass / 1 = validation failed / 2 = usage or input problem (missing file,
empty set, and similar)
"""

import argparse
import re
import sys
from pathlib import Path

# A verdict row: `S01 | supported | …`. Tolerates a leading pipe, whitespace, and an emoji
# before the label (✅/⚠️/❌). Deliberately does **not** match a range like `S01–S19` — what
# follows S01 there is a dash, not a separator, so the regex rejects it for free.
VERDICT_ROW = re.compile(
    r"^\s*\|?\s*(S\d+)\s*\|\s*[^\w\s|]*\s*(supported|unverifiable|conflict)\b",
    re.IGNORECASE,
)

# The machine-readable self-declared count. Deliberately an ASCII key rather than a prose
# phrasing like "N sentences received" — prose gets falsely matched by any "N sentences"
# appearing elsewhere in the body, which is far too brittle to build a gate on.
DECLARED = re.compile(r"^\s*input_sentence_count\s*:\s*(\d+)\s*$", re.IGNORECASE | re.MULTILINE)

# Sentence IDs in the authoritative list: the first token of each line. Accepts both
# `S01\tfact\t…` and `S01 | fact | …`.
INPUT_ID = re.compile(r"^\s*\|?\s*(S\d+)\b")


def parse_expected(path: Path) -> list[str]:
    """The authoritative input set. Order is preserved (so missing IDs are reported in the
    original order); a duplicate here is an error by the party that produced the list."""
    ids: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = INPUT_ID.match(line)
        if m:
            ids.append(m.group(1).upper())
    return ids


def parse_actual(path: Path) -> list[str]:
    """Per-sentence verdict rows in audit.md, in order of appearance (duplicates kept, so
    they can be detected)."""
    return [
        m.group(1).upper()
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if (m := VERDICT_ROW.match(raw))
    ]


def parse_declared(path: Path) -> int | None:
    m = DECLARED.search(path.read_text(encoding="utf-8", errors="replace"))
    return int(m.group(1)) if m else None


def _fmt(ids) -> str:
    """Keep failures readable: truncate past 12 entries, but always state the true total."""
    ids = list(ids)
    head = ", ".join(ids[:12])
    return f"{head}{f' … ({len(ids)} total)' if len(ids) > 12 else ''}"


def validate(expected_path: Path, audit_path: Path) -> tuple[int, list[str]]:
    """→ (exit_code, message lines). Messages address whoever has to fix this, so they name
    the specific IDs rather than reporting a count."""
    msgs: list[str] = []

    if not expected_path.is_file():
        return 2, [f"❌ audit gate: authoritative input list not found → {expected_path}",
                   "   The orchestrator must write the topic-sentence list to audit-input.tsv"
                   " **before** dispatching the reviewer.",
                   "   Without it there is no trustworthy baseline — and taking the count"
                   " declared inside audit.md as the baseline is the exact hole that was bypassed."]
    if not audit_path.is_file() or audit_path.stat().st_size == 0:
        return 2, [f"❌ audit gate: audit.md missing or empty → {audit_path}"]

    expected = parse_expected(expected_path)
    if not expected:
        return 2, [f"❌ audit gate: no sentence_id parsed from {expected_path.name}"
                   " (each line should start with an ID such as S01)"]

    dup_expected = sorted({i for i in expected if expected.count(i) > 1})
    if dup_expected:
        return 2, [f"❌ audit gate: the authoritative input list itself contains duplicate IDs:"
                   f" {_fmt(dup_expected)}",
                   "   That is an error made while extracting topic sentences. Fix the list,"
                   " then re-dispatch the reviewer."]

    expected_set = set(expected)
    actual = parse_actual(audit_path)
    actual_set = set(actual)

    declared = parse_declared(audit_path)
    if declared is None:
        msgs.append("❌ audit gate: audit.md does not declare `input_sentence_count: N`"
                    " (must be on its own line, ASCII key)")
        msgs.append("   The self-declared count is still required — as the thing being checked."
                    " It exposes the gap between what the reviewer thought it received and what"
                    " was actually sent.")
    elif declared != len(expected_set):
        msgs.append(f"❌ audit gate: audit.md declares {declared} sentence(s) received,"
                    f" the authoritative list has {len(expected_set)}")
        msgs.append("   What the reviewer received differs from what was dispatched — check"
                    " whether the task template dropped sentences.")

    if not actual:
        msgs.append("❌ audit gate: audit.md contains no per-sentence verdict rows")
        msgs.append("   Expected format: `S01 | supported | …`, one row per sentence."
                    " A range summary (`S01–S19 | supported ×19`) does not count.")

    dup_actual = sorted({i for i in actual if actual.count(i) > 1})
    if dup_actual:
        msgs.append(f"❌ audit gate: duplicate sentence_id in the verdict rows: {_fmt(dup_actual)}")
        msgs.append("   Repetition pads the row count while still leaving other sentences"
                    " unjudged — precisely what a gate that only counts rows cannot catch.")

    missing = [i for i in expected if i not in actual_set]
    if missing:
        msgs.append(f"❌ audit gate: {len(missing)} sentence(s) have no verdict → {_fmt(missing)}")

    extra = sorted(actual_set - expected_set)
    if extra:
        msgs.append(f"❌ audit gate: verdict rows contain IDs absent from the authoritative"
                    f" list → {_fmt(extra)}")
        msgs.append("   The reviewer should not invent sentences. Most likely it pulled in"
                    " other sentences from the draft.")

    if msgs:
        msgs.append("")
        msgs.append("   One sentence, one row is a hard contract: as many rows out as"
                    " sentences in, with IDs corresponding one-to-one.")
        msgs.append("   Re-dispatch the reviewer, one row per sentence. If it fails again,"
                    " mark the whole run `partial` — never deliverable.")
        return 1, msgs

    return 0, [f"✅ audit completeness: all {len(expected_set)} sentence(s) judged individually,"
               " IDs correspond one-to-one, no duplicates, none out of range"]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--expected", required=True,
                   help="authoritative input list (audit-input.tsv), written by the"
                        " orchestrator before the reviewer is dispatched")
    p.add_argument("--audit", required=True, help="the reviewer's output (audit.md)")
    p.add_argument("--quiet", action="store_true", help="print only on failure")
    a = p.parse_args()

    code, msgs = validate(Path(a.expected).expanduser(), Path(a.audit).expanduser())
    if code != 0 or not a.quiet:
        print("\n".join(msgs), file=sys.stderr if code != 0 else sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())
