# Worked example: what the gates actually do

> **This is an illustrative example.** The claims and sources below are synthetic,
> chosen to show the *ledger format and the gate behavior* — not a real research
> run. It exists so you can see, before installing, exactly how a confirmed, a
> quarantined, and an unresolved claim are recorded and judged.

**Research question:** *"When do the EU AI Act's obligations for general-purpose AI (GPAI) models take effect, and how large is the compliance fine ceiling?"*

After a Quick Recon, three central claims land in the **Claim Ledger**. Each row below uses the ledger schema (`claim_id / normalized_claim / importance / risk_reason / source_family / locator / status / merged_from / counterquery`). Watch what the gate does to each.

---

### Claim 1 — `confirmed` (reaches the conclusions)

```yaml
claim_id: ex-A1
normalized_claim: "GPAI obligations under the EU AI Act apply from 2 August 2025."
importance: central
risk_reason: "policy/legal effective date, central to the answer"
source_family: regulator
locator: "Art. 113(b), OJ applicability section"
status: confirmed
merged_from: 0
counterquery: null             # already primary-sourced; no reverse search needed
```

A regulator-level primary source with a locator. **It clears the gate** and can be
stated as a conclusion.

---

### Claim 2 — `weak`, quarantined (mentioned, never concluded)

```yaml
claim_id: ex-A2
normalized_claim: "GPAI non-compliance fines reach up to EUR 35 million."
importance: central
risk_reason: "high-stakes figure — a large fine ceiling"
source_family: aggregate       # a news roundup repeating a number
locator: null                  # no primary citation; article number never given
status: weak
merged_from: 4                 # 4 reposts collapsed to one entry
counterquery: "EU AI Act Article 101 penalties GPAI fine ceiling"
```

The EUR 35M figure is real-*sounding* and widely repeated — but every copy is an
aggregator with no primary citation. **Four reposts are one source.** The gate marks
it `weak` and moves it to the report's *"To be verified"* list. It may be
**mentioned**, but it will **not** appear in a conclusion until the Regulation's
penalty article is read directly.

---

### Claim 3 — `unresolved` after a bounce (never stated as fact)

```yaml
claim_id: ex-A3
normalized_claim: "GPAI providers must retrain non-compliant models within 6 months."
importance: central
risk_reason: "central obligation with no regulatory text located"
source_family: community       # a forum comment
locator: null                  # nothing to point at
status: unresolved
merged_from: 0
counterquery: "EU AI Act GPAI remediation timeline obligation text"
```

A `central` claim with **no primary-source locator**. Rather than let it ride into
the report on faith, the gate first **sends it back for a targeted Round 2 search**.
Round 2 still finds no regulatory text — so the claim stays `unresolved`: shown under
*"pending verification,"* not stated as fact. Note what the gate does **not** do — it
never declares the obligation false. Absence of evidence is `unresolved`, not
`refuted`.

---

## How the three map to what you receive

| Claim | Source family | Ledger status | Where it lands |
|-------|---------------|---------------|----------------|
| Effective date (ex-A1) | `regulator` (primary) | `confirmed` | A conclusion in the report |
| EUR 35M fine (ex-A2) | `aggregate` (×4 reposts) | `weak` | "To be verified" list, not concluded |
| 6-month retraining (ex-A3) | `community` | `unresolved` | "Pending verification"; not stated as fact |

The report you receive reads normally. The difference is what *didn't* make it in as
fact: a plausible number nobody could source, and a plausible obligation with no text
behind it — neither stated as a conclusion, and neither declared false. That is the
whole point — see [The Claim Ledger Method](../docs/claim-ledger-method.md).
