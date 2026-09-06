---
name: research
description: "Use when the user asks to research, investigate, compare competitors, study a market or industry, check the current status of a regulation or policy, search literature, or simply look something up that needs external sources. Any question that requires fetching outside information triggers this skill. To verify specific claims in an existing report, use a dedicated verification pass instead."
---

> ✦ **GiaSip** · github.com/GiaSip/giasip-skills

# GiaSip Research

**Goal.** Get the user accurate information that answers *their* question. Accuracy is a hard constraint; breadth is a means (you must gather widely to hit the accurate parts).

**Method.** Split the question into 2–3 complementary facets and run one sub-agent per facet in parallel. Sub-agents only gather, they do not conclude. Each sub-agent stops after at most 15 searches/fetches and returns compact findings without writing files. The main agent then writes a single `report.md`: answer the user's questions one by one, list every entity found with its URL, keep the body under 200 lines, and end with a separate **"To verify"** section.

**Discipline (hard rules)**
- Every fact carries a source URL. Prefer official / owner primary sources; label source type (primary / third-party / media).
- If it cannot be found, write "not found" — never fill from memory. Dates are absolute. GitHub stars and timestamps come from `gh api` snapshots, not search-result pages.
- Read and write only inside the output directory. Never `rm -rf`.
- Before anything goes out under a real name, quotes a price, or states a legal/financial conclusion, run a verification pass on the claims.

**Meta-rule.** This skill only changes in response to a human comment made at the point of use (kept in `FEEDBACK.md` beside it). AI review feedback never edits it directly. Two controlled runs (2026-09-05/06) showed that growing this skill from 0 to 144 to 433 lines left precision flat, narrowed recall, and cost 6–13× more.
