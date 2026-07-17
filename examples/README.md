# Worked example: what the gates actually do

> **This is an illustrative example.** The claims and sources below are synthetic,
> chosen to show the *format and the gate behavior* — not a real research run. It
> exists so you can see, before installing, exactly what a ClaimCard, a bounced
> claim, and a quarantined claim look like.

**Research question:** *"When do the EU AI Act's obligations for general-purpose AI (GPAI) models take effect, and how large is the compliance fine ceiling?"*

After a Quick Recon, three central claims land in the ledger. Watch what happens to each.

---

### Claim 1 — confirmed (reaches the conclusions)

```yaml
claim_id: ex-A1
claim: "GPAI obligations under the EU AI Act apply from 2 August 2025."
importance: central
claim_type: factual
source_type: regulator
source_url: https://eur-lex.europa.eu/eli/reg/2024/1689/oj
evidence: "Art. 113(b) — locator: OJ applicability section"
confidence: high
status: confirmed
```

A regulator-level primary source with a locator. **It clears the gate** and can be
stated as a conclusion.

---

### Claim 2 — quarantined `weak` (mentioned, never concluded)

```yaml
claim_id: ex-A2
claim: "Non-compliance fines for GPAI reach up to EUR 35 million."
importance: central
claim_type: metric
source_type: aggregate       # a news roundup repeating a figure
evidence: "figure appears across 4 blog summaries; no article number cited"
confidence: low
status: weak
merged_from: 4               # 4 reposts collapsed to 1 entry
counterquery: "EU AI Act Article 99 penalties GPAI fine ceiling"
```

The EUR 35M number is real-*sounding* and widely repeated — but every copy is an
aggregator with no primary citation. **Five reposts are one source.** The gate
marks it `weak` and moves it to the report's *"To be verified"* list. It will be
**mentioned**, but it will **not** appear in a conclusion sentence until a primary
source (the Regulation's penalty article) is read directly.

---

### Claim 3 — bounced (never enters the report as-is)

```yaml
claim_id: ex-A3
claim: "GPAI providers must retrain non-compliant models within 6 months."
importance: central
claim_type: factual
source_type: community       # a forum comment
evidence: "paraphrase in a discussion thread; no source linked"
confidence: low
status: bounced -> Round 2
gap: "no regulatory text found for a '6-month retraining' obligation"
counterquery: "EU AI Act GPAI remediation timeline obligation text"
```

A `central` claim with **no primary-source locator**. Rather than let it ride into
the report on faith, the gate **bounces it back for a second, targeted search
round** using the `counterquery`. If Round 2 still finds no regulatory text, the
claim is dropped — not softened into a vague sentence.

---

## How the three map to what you receive

| Claim | Source family | Gate verdict | Where it lands |
|-------|---------------|--------------|----------------|
| Effective date (ex-A1) | `regulator` (primary) | `confirmed` | A conclusion in the report |
| EUR 35M fine (ex-A2) | `aggregate` (×4 reposts) | `weak` | "To be verified" list, not concluded |
| 6-month retraining (ex-A3) | `community` | `bounced` | Round 2, or dropped |

The report you receive reads normally. The difference is what *didn't* make it in:
a plausible number nobody could source, and a plausible obligation that doesn't
exist in the text. That is the whole point — see [The Claim Ledger Method](../docs/claim-ledger-method.md).
