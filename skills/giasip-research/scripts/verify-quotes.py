#!/usr/bin/env python3
"""Quote gate — every verbatim quote is matched against the **source snapshot**.

## Why this exists

The ClaimCard schema has always demanded a verbatim `quote` copied out of the text the
worker actually fetched. Nothing checked it. In practice a run would deliver with every
`source_sha256: unavailable` and every quote one paraphrase layer away from the source,
and the only thing between that and the final report was a reviewer reading prose.
Deterministic string matching is free; reviewer attention is not. So the cheap check runs
first and the reviewer only sees what it could not settle — the cascade pattern
(deterministic matching first, judgment only on the remainder).

## What it compares against — and why that choice is the whole point

Each quote is compared to its **snapshot**: the normalized main text of the source,
persisted at capture time under `<run_dir>/snapshots/`.

It must **never** be pointed at `<run_dir>/artifacts/*`. Those are the worker's own
output. A quote "verified" against the artifact that produced it is circular
self-justification — the audited party supplying its own answer key, the same hole
`validate-audit.py` exists to close. A quote a worker invented and then faithfully copied
into its artifact would pass such a check with full marks. Snapshot paths are therefore
confined to the run directory and rejected if they point into `artifacts/`.

## The input is a strict machine-readable contract, not a parsed ledger

**`<run_dir>/quotes.tsv`, written by the orchestrator before the gate runs**, one row per
claim, tab-separated, with this exact header:

    claim_id	importance	evidence_kind	quote	snapshot	source_sha256	source_url

The first version of this checker parsed `ledger.md` directly and tried to be tolerant of
Markdown: `key: value` blocks *and* pipe tables. An adversarial review found what
tolerance costs. A ledger holding one well-formed block plus one **valid** GFM table that
omitted its outer pipes silently dropped the table's rows — including a fabricated quote —
and the gate printed `checked 1 claim(s): 1 quote_ok` with exit 0. Escaped pipes shifted
columns; `- **claim_id:** c1` parsed the ID as `** c1`; duplicate IDs merged in silence.
Every one of those failures was *invisible*, and the only coverage number printed was the
parser's own — which is the audited party supplying the baseline all over again.

So this gate does not guess. **Any malformed line is a hard input error, never a skipped
row.** If a row cannot be parsed, nothing is reported as passing.

## Design boundary (stated honestly — do not oversell this)

Given a snapshot that was captured independently and is accepted as authoritative, this
gate shows the quote is a substring of that snapshot's normalized text, and that the
snapshot still hashes to what the ledger recorded.

It does **not** show: that the snapshot came from `source_url`; that quote, snapshot and
hash were not fabricated together by the same party (they usually are produced by the same
worker — the defense against that is capturing snapshots outside the worker's control, not
this script); that `retrieved_at` is truthful; that main-text extraction was complete; or
that the source **supports the claim**. A real sentence quoted out of context passes here
and must still be caught downstream.

`--check-urls` reports reachability separately and **never as evidence**. A 200 means a
server answered, not that the page says what the claim says.

exit codes: 0 = pass / 1 = verification failed / 2 = usage or input problem (missing
files, malformed rows, duplicate IDs, unusable snapshot directory)
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from pathlib import Path

HEADER = (
    "claim_id",
    "importance",
    "evidence_kind",
    "quote",
    "snapshot",
    "source_sha256",
    "source_url",
)

# No path separators, no glob metacharacters, no leading dot: the ID becomes part of a
# filesystem lookup, and `../` or `*` in it would let a claim fetch its answer from
# outside the snapshot directory.
CLAIM_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SHA16 = re.compile(r"^[0-9a-f]{16}$", re.IGNORECASE)

# `unavailable:<method>` in the snapshot column is the escape hatch the ClaimCard schema
# already grants: a host that could read a page but could not hand over a hashable full
# body. It is legitimate, it is *not* verifiable, and it must never be reported as verified.
CAPTURE_METHODS = {
    "reader-mode",
    "raw-html",
    "pdf-text-layer",
    "ocr",
    "api-json",
    "search-snippet-only",
}

# Enforced from the worker template: "≥8 consecutive words, or ≥15 chars for CJK". A
# one-word "quote" is a substring of almost any page — it would turn the gate green while
# anchoring nothing.
MIN_WORDS = 8
MIN_CJK_CHARS = 15
CJK = re.compile(r"[㐀-鿿豈-﫿\U00020000-\U0002ebef]")


class InputError(Exception):
    """A malformed contract. Never downgraded to a skipped row."""


def normalize(text: str) -> str:
    """The skill's fixed normalization algorithm, applied in order. Two hosts that
    normalize differently hash an unchanged page to different values, which reads as false
    drift — so this is a spec, not a preference:

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
    """Line breaks are a layout artifact of the source, not of the sentence. A quote copied
    across a wrapped line must still match, so matching happens on one line. This affects
    matching only — never the hash."""
    return re.sub(r"\s+", " ", normalized.replace("\n", " ")).strip()


def quote_long_enough(quote: str) -> bool:
    if len(CJK.findall(quote)) >= MIN_CJK_CHARS:
        return True
    return len(quote.split()) >= MIN_WORDS


def parse_quotes_tsv(path: Path) -> list[dict[str, str]]:
    """Strict. Every deviation raises; nothing is silently skipped."""
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise InputError(f"{path.name} is not valid UTF-8 ({exc})") from exc

    lines = [
        line for line in raw.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if not lines:
        raise InputError(f"{path.name} contains no rows")

    header = tuple(c.strip() for c in lines[0].split("\t"))
    if header != HEADER:
        raise InputError(
            f"{path.name} header must be exactly:\n    " + "\t".join(HEADER)
            + f"\n  got:\n    " + "\t".join(header)
        )

    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for lineno, line in enumerate(lines[1:], start=2):
        cells = line.split("\t")
        if len(cells) != len(HEADER):
            raise InputError(
                f"{path.name}:{lineno} has {len(cells)} column(s), expected {len(HEADER)}."
                " Tabs and newlines inside a quote must be written as single spaces —"
                " matching is whitespace-insensitive, so nothing is lost."
            )
        row = {k: v.strip() for k, v in zip(HEADER, cells)}
        cid = row["claim_id"]

        if not CLAIM_ID.match(cid):
            raise InputError(
                f"{path.name}:{lineno} claim_id {cid!r} is not a bare identifier"
                " ([A-Za-z0-9][A-Za-z0-9._-]*). It is used as a filename; path separators"
                " and glob characters are refused rather than resolved."
            )
        if cid in seen:
            raise InputError(
                f"{path.name}:{lineno} duplicate claim_id {cid!r}. A duplicate silently"
                " overwrites a claim and pads the checked count — the same evasion the"
                " audit gate rejects."
            )
        seen.add(cid)

        if row["evidence_kind"] not in ("quote", "locator"):
            raise InputError(
                f"{path.name}:{lineno} evidence_kind must be exactly `quote` or `locator`,"
                f" got {row['evidence_kind']!r}. An implicit kind is what makes an"
                " unanchored claim indistinguishable from an unquotable one."
            )

        if row["evidence_kind"] == "quote":
            if not row["quote"]:
                raise InputError(
                    f"{path.name}:{lineno} evidence_kind is `quote` but the quote is empty."
                    " An empty string is a substring of everything; it would be reported as"
                    " verified while anchoring nothing. Use `locator` when there is no quote."
                )
            if not quote_long_enough(row["quote"]):
                raise InputError(
                    f"{path.name}:{lineno} quote is shorter than the template minimum"
                    f" (≥{MIN_WORDS} consecutive words, or ≥{MIN_CJK_CHARS} CJK chars):"
                    f" {row['quote']!r}"
                )
            if not row["snapshot"]:
                raise InputError(
                    f"{path.name}:{lineno} evidence_kind is `quote` but no snapshot is"
                    " given. Use `unavailable:<capture_method>` when the host could read"
                    " the source but could not hand over a hashable body —"
                    f" method one of: {', '.join(sorted(CAPTURE_METHODS))}."
                )
            if row["snapshot"].startswith("unavailable:"):
                method = row["snapshot"].split(":", 1)[1]
                if method not in CAPTURE_METHODS:
                    raise InputError(
                        f"{path.name}:{lineno} unknown capture_method {method!r};"
                        f" expected one of: {', '.join(sorted(CAPTURE_METHODS))}"
                    )

        if row["source_sha256"] and row["source_sha256"].lower() != "unavailable":
            if not SHA16.match(row["source_sha256"]):
                raise InputError(
                    f"{path.name}:{lineno} source_sha256 must be 16 hex chars or"
                    f" `unavailable`, got {row['source_sha256']!r}"
                )
        rows.append(row)

    if not rows:
        raise InputError(f"{path.name} has a header but no claim rows")
    return rows


def resolve_snapshot(run_dir: Path, snapshots: Path, value: str) -> Path:
    """Snapshot paths stay inside the run directory and out of `artifacts/`. The second
    rule is not paranoia about traversal — it is the point of the gate: an artifact is the
    audited party's own output, so accepting one as the answer key restores the circularity
    this script exists to break."""
    candidate = Path(value)
    resolved = (snapshots / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    root = run_dir.resolve()
    if root not in resolved.parents and resolved != root:
        raise InputError(
            f"snapshot path escapes the run directory: {value!r} → {resolved}"
        )
    if "artifacts" in resolved.relative_to(root).parts:
        raise InputError(
            f"snapshot path points into artifacts/: {value!r}. Checking a quote against the"
            " artifact that produced it is circular self-justification."
        )
    return resolved


def check_url(url: str, timeout: float) -> str:
    import urllib.error
    import urllib.request

    agent = {"User-Agent": "verify-quotes/2.0"}
    try:
        with urllib.request.urlopen(
            urllib.request.Request(url, method="HEAD", headers=agent), timeout=timeout
        ) as resp:
            return f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 405, 501):                  # HEAD refused; a GET may still work
            try:
                with urllib.request.urlopen(
                    urllib.request.Request(url, headers=agent), timeout=timeout
                ) as resp:
                    return f"HTTP {resp.status}"
            except Exception as inner:                   # noqa: BLE001
                return f"error: {type(inner).__name__}"
        return f"HTTP {exc.code}"
    except Exception as exc:                             # noqa: BLE001
        return f"error: {type(exc).__name__}"


def verify(
    run_dir: Path, quotes_path: Path, snapshots: Path, urls: bool, timeout: float
) -> tuple[int, list[str]]:
    if not quotes_path.is_file():
        return 2, [
            f"❌ quote gate: {quotes_path} not found",
            "   The orchestrator writes it **before** running this gate, one row per claim:",
            "     " + "\t".join(HEADER),
            "   Rows are tab-separated; `locator` rows leave quote/snapshot empty; a quote"
            " that could not be hashed uses `unavailable:<capture_method>` in the snapshot"
            " column.",
        ]

    try:
        rows = parse_quotes_tsv(quotes_path)
    except InputError as exc:
        return 2, [f"❌ quote gate: {exc}",
                   "   Malformed rows are refused outright. A tolerant parser drops rows"
                   " silently, and a dropped row is indistinguishable from a passing one."]

    needs_snapshot = [r for r in rows
                      if r["evidence_kind"] == "quote"
                      and not r["snapshot"].startswith("unavailable:")]
    if needs_snapshot and not snapshots.is_dir():
        return 2, [f"❌ quote gate: snapshot directory not found → {snapshots}",
                   f"   {len(needs_snapshot)} quote(s) name a snapshot there. A missing"
                   " directory is an input problem, not a per-claim verdict — reporting it"
                   " as N individual failures would bury the fact that nothing was checked."]

    out: list[str] = []
    failures = 0
    unverifiable = 0
    counts = {"ok": 0, "locator": 0}

    for row in rows:
        cid, kind = row["claim_id"], row["evidence_kind"]

        if kind == "locator":
            counts["locator"] += 1
            out.append(f"·  {cid} | skipped (locator — nothing to match verbatim)")
            continue

        if row["snapshot"].startswith("unavailable:"):
            unverifiable += 1
            method = row["snapshot"].split(":", 1)[1]
            out.append(
                f"⚠️  {cid} | unverifiable_capture | {method}"
                "  (explained: legitimate, but this gate verified nothing here)"
            )
            continue

        try:
            path = resolve_snapshot(run_dir, snapshots, row["snapshot"])
        except InputError as exc:
            return 2, [f"❌ quote gate: {exc}"]

        if not path.is_file():
            failures += 1
            out.append(f"❌ {cid} | no_snapshot | {path} does not exist")
            continue

        try:
            raw = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            failures += 1
            out.append(f"❌ {cid} | snapshot_not_utf8 | {path.name}: {exc}")
            continue

        text = normalize(raw)
        if raw.strip("\n") != text:
            failures += 1
            out.append(
                f"❌ {cid} | snapshot_not_normalized | {path.name}\n"
                "     A snapshot must be stored as the exact normalized bytes that were"
                " hashed. If the file still needs normalizing, the hash in the ledger was"
                " taken from something other than what is on disk."
            )
            continue

        declared = row["source_sha256"].lower()
        if declared and declared != "unavailable":
            got = hash16(text)
            if declared != got:
                failures += 1
                out.append(
                    f"❌ {cid} | snapshot_hash_mismatch | ledger {declared} vs snapshot {got}\n"
                    "     The snapshot was edited after capture, or the hash was recorded"
                    " from different bytes. Either way the anchor no longer anchors."
                )
                continue

        if flatten(normalize(row["quote"])) in flatten(text):
            counts["ok"] += 1
            out.append(f"✅ {cid} | quote_ok | {path.name}")
        else:
            failures += 1
            out.append(
                f"❌ {cid} | quote_not_found | {path.name}\n"
                "     The quote is not a substring of the captured source text. Either it"
                " was retyped from memory or paraphrased through a reader, or the snapshot"
                " is of a different page."
            )

        if urls and row["source_url"]:
            out.append(
                f"   ↪ url {check_url(row['source_url'], timeout)}"
                "  (reachability only — never counts as support)"
            )

    out.append("")
    out.append(
        f"checked {len(rows)} claim(s) from {quotes_path.name}: {counts['ok']} quote_ok,"
        f" {failures} failed, {unverifiable} unverifiable_capture,"
        f" {counts['locator']} locator"
    )

    if failures:
        out.append("")
        out.append(
            "   Failures are the reviewer's queue — send these, not the whole ledger. A"
            " quote that cannot be found in its own source is not a wording problem; treat"
            " the claim as unanchored until it is re-captured."
        )
        return 1, out

    if unverifiable:
        out.append(
            f"   ⚠️ {unverifiable} quote(s) could not be machine-checked at all (capture"
            " explained but no hashable body). They need manual review; do not read this"
            " exit code as 'all quotes verified'."
        )
    if counts["ok"]:
        out.append(
            "   Boundary: given snapshots accepted as authoritative, each quote above is a"
            " substring of one. This says nothing about whether the source supports the"
            " claim, nor whether quote and snapshot were fabricated together."
        )
    return 0, out


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--run-dir", type=Path, required=True,
                   help="run directory holding quotes.tsv and snapshots/")
    p.add_argument("--quotes", type=Path, help="override: path to quotes.tsv")
    p.add_argument("--snapshots", type=Path,
                   help="override: snapshot directory (must stay inside --run-dir)")
    p.add_argument("--check-urls", action="store_true",
                   help="additionally report source_url reachability (network); reported"
                        " separately, never counted as support")
    p.add_argument("--timeout", type=float, default=10.0, help="per-URL timeout seconds")
    p.add_argument("--quiet", action="store_true", help="print only on failure")
    a = p.parse_args()

    run_dir = a.run_dir.expanduser()
    quotes = (a.quotes or (run_dir / "quotes.tsv")).expanduser()
    snapshots = (a.snapshots or (run_dir / "snapshots")).expanduser()

    code, msgs = verify(run_dir, quotes, snapshots, a.check_urls, a.timeout)
    if code != 0 or not a.quiet:
        print("\n".join(msgs), file=sys.stderr if code != 0 else sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())
