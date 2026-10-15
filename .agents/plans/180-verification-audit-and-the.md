# Plan: F118, verification audit and the record of the full run (Issue #180)

Documents, measurements, and tests that assert the audit's facts. No change to
CI, checks, scripts, prompts, or ADRs.

## Steps

1. **Measurements.** Read the `build` and `integration` jobs of the runs named
   in `docs/roadmap.md` ("State at the change cycle
   `pbc-planning-change-four-workstreams`") and of the three one-lesson pull
   requests of F61 from the Actions API: step times, cache hits and misses,
   the phases of the group `build`, and the completion time of each test file
   of `integration`.
2. **Audit record** `docs/verification-audit.md`: the call graph, the verdict
   on the preview test, the validity domains of the check identity, the
   division of `integration`, the inventory of local build obligations, and
   the proposal for the owner.
3. **Measurement record** in `docs/release-readiness.md`: full runs at 22, 28,
   and 32 lessons with cache state, the one-lesson pull requests, growth per
   lesson, projections (labelled), judged against ADR 015.
4. **Tests** `tests/integration/test_verification_audit.py`: the audit's
   facts hold in the code (builds per check, what each comparison covers,
   every input of the identity classified, the proposed `integration` parts
   run every test file once).
5. **Proposal on the Issue** for the owner (timeout and covered lesson count).
6. Records: handoff, completion, summary; `./scripts/verify.sh` last.
