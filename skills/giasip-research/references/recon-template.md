# Recon Template — Compatibility Pointer

The maintained Round 1 and Round 2 worker contracts now live in
[`subagent-templates.md`](subagent-templates.md), including ClaimCard fields,
`ledger_patch`, and the Adjudication `hypothesis_patch`.

Compatibility adapters may continue opening this file during migration, but must
load `subagent-templates.md` before dispatching a worker. Do not duplicate the
template here.
