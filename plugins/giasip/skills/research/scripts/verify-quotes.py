#!/usr/bin/env python3
"""Quote pre-check — every verbatim quote is matched against the **source snapshot**.

## Why this exists

The ClaimCard schema has always demanded a verbatim `quote` copied out of the text the
worker actually fetched. Nothing checked it. In practice a run would deliver with every
`source_sha256: unavailable` and every quote one paraphrase layer away from the source,
and the only thing standing between that and the final report was a reviewer reading
prose. Deterministic string matching is free; reviewer attention is not. So the cheap
check runs first and the reviewer only sees what it could not settle — the cascade
pattern (deterministic field matching first, LLM judgment only on the ambiguous
remainder) rather than sending everything to the expensive layer.

## What it compares against — and why that choice is the whole point

It compares the quote to `<run_dir>/snapshots/<claim_id>.txt`: **the normalized main text
of the source**, persisted at capture time.

It deliberately does **not** compare against `<run_dir>/artifacts/*.md`. Those are the
worker's own output. A quote "verified" against the artifact that produced it is
circular self-justification — the audited party supplying its own answer key, exactly
the hole `validate-audit.py` was written to close after a reviewer declared its own
sentence count and passed. A quote that a worker invented and then faithfully copied
into its artifact would sail through such a check with full marks.

## Design boundary (stated honestly, same as the audit gate)

This validates that the quote **appears in the source text**. It does not validate that
the source **supports the claim** — a real sentence quoted out of context passes here and
should still be caught downstream. It also does not validate that the snapshot is of the
right page; that is what `source_sha256` + `source_url` are for, and the hash check below
only tells you the snapshot has not been edited since capture.

`--check-urls` reports reachability **separately and never as evidence**. A 200 says a
server answered, not that the page says what the claim says. Reachability is reported so
that a dead link is visible, not so that a live one counts for anything.

exit codes: 0 = pass / 1 = verification failed / 2 = usage or input problem (missing
files, nothing parsed, and similar)
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from pathlib import Path

FIELDS = {
    "claim_id",
    "normalized_claim",
    "claim",
    "importance",
    "risk_reason",
    "source_family",
    "source_type",
    "source_url",
    "locator",
    "evidence_kind",
    "evidence",
    "quote",
    "capture_anchor",
    "source_sha256",
    "retrieved_at",
    "status",
}

# `- **claim_id**: r0712-market-A1`, `claim_id: …`, `| claim_id | … |` all reach the same
# parser. Markdown decoration is stripped rather than matched, because a ledger is written
# by hand and the exact bolding is not something to build a gate on.
KV = re.compile(
    r"^\s*(?:[-*+]\s*)?[`*_]*([A-Za-z_][A-Za-z0-9_]*)[`*_]*\s*[:：]\s*(.*)$"
)
TABLE_SEP = re.compile(r"^\s*\|?[\s:|-]+\|[\s:|-]*$")
SHA16 = re.compile(r"\b([0-9a-f]{16})\b", re.IGNORECASE)


def strip_md(value: str) -> str:
    """Values arrive wrapped in backticks, bold markers or quotes; the content is what
    matters. Applied to field values only — never to snapshot text."""
    value = value.strip()
    for _ in range(3):
        stripped = value.strip()
        if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in "`\"'":
            value = stripped[1:-1]
            continue
        if stripped.startswith("**") and stripped.endswith("**") and len(stripped) > 4:
            value = stripped[2:-2]
            continue
        break
    return value.strip()


def normalize(text: str) -> str:
    """The skill's fixed normalization algorithm, applied in order. Two hosts that
    normalize differently hash an unchanged page to different values, which reads as
    false drift — so this is a spec, not a preference:

    ① extracted main text (the caller's job) ② Unicode NFC ③ line endings → \\n
    ④ strip each line ⑤ collapse whitespace runs to one space ⑥ drop empty lines
    """
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"\s+", " ", line.strip())
        if line:
            lines.append(line)
    return "\n".join(lines)


def hash16(normalized: str) -> str:
    """⑦ UTF-8 → sha256 → first 16 hex chars."""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def flatten(normalized: str) -> str:
    """Line breaks are a layout artifact of the source, not of the sentence. A quote
    copied across a wrapped line must still match, so matching happens on one line."""
    return re.sub(r"\s+", " ", normalized.replace("\n", " ")).strip()


def parse_table(lines: list[str]) -> list[dict[str, str]]:
    """Pipe-table ledgers: the header row naming `claim_id` defines the columns."""
    rows: list[dict[str, str]] = []
    header: list[str] | None = None
    for raw in lines:
        if not raw.strip().startswith("|"):
            header = None
            continue
        if TABLE_SEP.match(raw):
            continue
        cells = [strip_md(c) for c in raw.strip().strip("|").split("|")]
        keys = [c.lower().replace(" ", "_") for c in cells]
        if header is None:
            if "claim_id" in keys:
                header = keys
            continue
        row = {k: v for k, v in zip(header, cells) if k in FIELDS and v}
        if row.get("claim_id"):
            rows.append(row)
    return rows


def parse_blocks(lines: list[str]) -> list[dict[str, str]]:
    """`key: value` ledgers: a new `claim_id` opens a new entry."""
    rows: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw in lines:
        if raw.strip().startswith("|"):
            continue
        m = KV.match(raw)
        if not m:
            continue
        key, value = m.group(1).lower(), strip_md(m.group(2))
        if key not in FIELDS:
            continue
        if key == "claim_id":
            if current:
                rows.append(current)
            current = {"claim_id": value}
        elif current is not None and value:
            current.setdefault(key, value)
    if current:
        rows.append(current)
    return [r for r in rows if r.get("claim_id")]


def parse_ledger(path: Path) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    rows = parse_table(lines) + parse_blocks(lines)
    seen: dict[str, dict[str, str]] = {}
    for row in rows:
        seen.setdefault(row["claim_id"], {}).update(
            {k: v for k, v in row.items() if v and k not in seen.get(row["claim_id"], {})}
        )
    return [dict(v, claim_id=k) for k, v in seen.items()]


def quote_of(row: dict[str, str]) -> str:
    return row.get("quote") or row.get("evidence") or ""


def declared_hash(row: dict[str, str]) -> str | None:
    for field in ("source_sha256", "capture_anchor"):
        value = row.get(field, "")
        if "unavailable" in value.lower():
            return None
        m = SHA16.search(value)
        if m:
            return m.group(1).lower()
    return None


def find_snapshot(snapshots: Path, claim_id: str) -> Path | None:
    if not snapshots.is_dir():
        return None
    exact = snapshots / f"{claim_id}.txt"
    if exact.is_file():
        return exact
    matches = sorted(p for p in snapshots.glob(f"{claim_id}.*") if p.is_file())
    return matches[0] if matches else None


def is_required(row: dict[str, str]) -> bool:
    """Capture discipline binds `central` and high-risk claims. A missing snapshot on a
    context-level claim is worth reporting, not worth failing the run over."""
    return row.get("importance", "").lower() == "central" or bool(
        row.get("risk_reason", "").strip()
    )


def check_url(url: str, timeout: float) -> str:
    import urllib.error
    import urllib.request

    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "verify-quotes/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 405, 501):                 # HEAD refused; a GET may still work
            try:
                get = urllib.request.Request(url, headers={"User-Agent": "verify-quotes/1.0"})
                with urllib.request.urlopen(get, timeout=timeout) as resp:
                    return f"HTTP {resp.status}"
            except Exception as inner:                   # noqa: BLE001
                return f"error: {type(inner).__name__}"
        return f"HTTP {exc.code}"
    except Exception as exc:                             # noqa: BLE001
        return f"error: {type(exc).__name__}"


def verify(ledger: Path, snapshots: Path, urls: bool, timeout: float) -> tuple[int, list[str]]:
    if not ledger.is_file():
        return 2, [f"❌ quote gate: ledger not found → {ledger}"]

    rows = parse_ledger(ledger)
    if not rows:
        return 2, [
            f"❌ quote gate: no claim parsed from {ledger.name}",
            "   Expected either `claim_id: …` field lines or a pipe table whose header"
            " names claim_id. Nothing parsed means nothing checked — which must not be"
            " reported as a pass.",
        ]

    out: list[str] = []
    failures: list[str] = []
    counts = {"ok": 0, "locator": 0, "no_snapshot": 0, "not_found": 0, "hash_mismatch": 0}

    for row in sorted(rows, key=lambda r: r["claim_id"]):
        cid = row["claim_id"]
        kind = row.get("evidence_kind", "").lower()
        quote = quote_of(row)

        if kind == "locator" or (not quote and kind != "quote"):
            counts["locator"] += 1
            out.append(f"·  {cid} | skipped ({kind or 'no quote recorded'})")
            continue

        snapshot = find_snapshot(snapshots, cid)
        if snapshot is None:
            counts["no_snapshot"] += 1
            line = f"{cid} | no_snapshot | expected {snapshots}/{cid}.txt"
            if is_required(row):
                failures.append(line)
                out.append(f"❌ {line}  (central / high-risk — capture discipline binds)")
            else:
                out.append(f"⚠️  {line}  (not central / high-risk — reported, not failed)")
            continue

        text = normalize(snapshot.read_text(encoding="utf-8", errors="replace"))
        want = declared_hash(row)
        got = hash16(text)
        if want and want != got:
            counts["hash_mismatch"] += 1
            line = (
                f"{cid} | snapshot_hash_mismatch | ledger {want} vs snapshot {got}"
            )
            failures.append(line)
            out.append(
                f"❌ {line}\n     The snapshot was edited after capture, or the hash was"
                " recorded from different bytes. Either way the anchor no longer anchors."
            )
            continue

        if flatten(normalize(quote)) in flatten(text):
            counts["ok"] += 1
            out.append(f"✅ {cid} | quote_ok | {snapshot.name}")
        else:
            counts["not_found"] += 1
            line = f"{cid} | quote_not_found | {snapshot.name}"
            failures.append(line)
            out.append(
                f"❌ {line}\n     The quote is not a substring of the captured source"
                " text. Either it was retyped from memory / paraphrased through a reader,"
                " or the snapshot is of the wrong page."
            )

        if urls and row.get("source_url"):
            out.append(
                f"   ↪ url {check_url(row['source_url'], timeout)}"
                "  (reachability only — never counts as support)"
            )

    out.append("")
    out.append(
        f"checked {len(rows)} claim(s): {counts['ok']} quote_ok, {counts['not_found']}"
        f" not_found, {counts['hash_mismatch']} hash_mismatch, {counts['no_snapshot']}"
        f" missing snapshot, {counts['locator']} skipped (locator / no quote)"
    )

    if failures:
        out.append("")
        out.append(
            "   Failures are the reviewer's queue — send these to Mini Assurance, not the"
            " whole ledger. A quote that cannot be found in its own source is not a"
            " wording problem; treat the claim as unanchored until re-captured."
        )
        return 1, out

    out.append(
        "   Boundary: this says each quote appears in the captured source text. It does"
        " not say the source supports the claim."
    )
    return 0, out


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--run-dir", type=Path, help="run directory (implies ledger.md + snapshots/)")
    p.add_argument("--ledger", type=Path, help="override: path to ledger.md")
    p.add_argument("--snapshots", type=Path, help="override: snapshots directory")
    p.add_argument(
        "--check-urls",
        action="store_true",
        help="additionally report source_url reachability (network); reported separately,"
        " never counted as support",
    )
    p.add_argument("--timeout", type=float, default=10.0, help="per-URL timeout seconds")
    p.add_argument("--quiet", action="store_true", help="print only on failure")
    a = p.parse_args()

    if not a.run_dir and not (a.ledger and a.snapshots):
        p.error("give --run-dir, or both --ledger and --snapshots")

    run_dir = a.run_dir.expanduser() if a.run_dir else None
    ledger = (a.ledger or (run_dir / "ledger.md")).expanduser()
    snapshots = (a.snapshots or (run_dir / "snapshots")).expanduser()

    code, msgs = verify(ledger, snapshots, a.check_urls, a.timeout)
    if code != 0 or not a.quiet:
        print("\n".join(msgs), file=sys.stderr if code != 0 else sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())
