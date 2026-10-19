# Incremental `main`: the staged evidence (F120)

The evidence that ADR 017 (proposed) needs before the owner decides
question 9 of the requirements: whether a push to `main` may inherit the
executed results of unchanged lessons from the previous verified base of
`main`, with which mitigations. Produced by F120 (Issue #196) on
2026-10-16 without changing what `main` executes: every push to `main`
still executes every lesson (ADR 014 decision 4). The sources are the
Actions API and the retained artifacts of the runs named below, the F61
test suites, and a local run on the commit of the branch's base. Every
projection is labelled; every claim names what shows it. The summary and
the mitigations with values are in ADR 017, "Evidence (F120)".

## 1. The same-commit comparison

**Claim it supports.** A selective verification against an accepted base
publishes the site a full verification publishes on the same commit, up
to documented, provenance-specific differences, *when the inherited
results are valid*. It does not show that they are valid; that is what
the digest, the check identity, and the environment identity establish
per lesson (sections 2, 3, and 5), and what section 5 shows they do not
fully establish today.

**Commit.** `4894c4bcfad3d68bee64f53ede2a4fdbaead3b3f` (the merge of pull
request #195, the base of this branch), 32 lessons.

**The full verification.** Run 38876222290 on `main` (a push run;
`verify` succeeded 09:22:07 UTC; every lesson executed; `build` 25 min
52 s; the group `build` 24 min 32 s: `lean-build` 24 s, `site-build`
5 min 56 s, `determinism` 5 min 33 s, the reproduction of 32 lessons
12 min 37 s). Its artifacts: `github-pages` (id 12036343203, the site of
178 files), `built-site-record` (id 12036392944), and `verification-base`
(id 12036304446, digest
`sha256:f50dd996763d26edecd7323462ca2aee8b6b3a6f04908645e2c850ec2e241574`).

**The selective verification.** `./scripts/verify.sh --base <directory>`
on the same commit, on the developer's machine (macOS 15, arm64, the
pinned toolchains of `docs/development.md`: Python 3.14.7, Quarto
1.10.19, the locked packages, the same browser build), with that base
downloaded into the directory and the checkout at `4894c4b` (the tracked
files unchanged; untracked documents of this feature present, which the
provenance region reports, below). The selection reported "selective run
against base 2e456d6b471b: 1 of 32 lessons executed, 31 restored": the
check identity equals the base's and 31 input digests equal the base's,
so 31 lessons' executed results are inherited and every page is rendered
on this commit, as ADR 017 decision 1 would do on `main`. One lesson,
`mechanics/09-verifying-scientific-code`, was executed locally although
nothing changed: on the case-insensitive file system of macOS
`pbc.authoring.digest` resolves the imported name `CHECKS` of
`pbc.verification` to the file `checks.py` and adds an entry with that
label to the digest, which CI (Linux) does not have. That is a defect of
F61's digest on a developer's machine (it fails safe: the lesson is
over-executed, and the local selection differs from CI's for a lesson
that imports a name whose lower case is a module name); it is recorded
for a follow-up and it gives this comparison one locally executed lesson
beside the 31 inherited ones. The run built the site (`site-build`) and
`determinism` passed on the copy. Of the run's other checks,
`check-tests-other` failed on
`tests/integration/test_verification_audit.py::test_a_lesson_executes_three_times_in_a_full_run`,
an F119 test that collects the reproduction tests from the repository
root while the run's selection file exists and so counts 1 lesson
instead of 32; it passes in CI, where that job has no base, and it fails
on every local `--base` run (recorded for a follow-up of F119); and
`site-checks-other` failed on
`tests/e2e/test_comparator.py::test_the_embedded_series_and_metrics_agree_with_a_fresh_run_of_pbc`,
which recomputes the gravitational-wave lesson's model series on the
checking machine and compares them with the data embedded in the page
(inherited from the base, computed on a runner) at a tolerance of 6e-6:
on this machine 25 of the 14,748 values differ by more than that (the
worst by 3.2e-5), identically for the CI site and the local site, since
both carry the same inherited data. That failure is the cross-machine
effect of section 5 reaching a check, not a difference between the two
sites, and it is recorded below under the residual risk. The run's other
21 checks passed. The site this run built is therefore the site of a
selective verification whose build, determinism, reproduction, and page
checks ran, not of a run that passed in full.

**The comparison** (the `github-pages` artifact against `site/_site` of
the local run; 178 files each): **98 files byte-identical, 79 differ, 1
file on each side under a different name.** The differing files by
kind, with their classification (every file by path follows the table):

| Files | What differs | Classification |
|---|---|---|
| 32 lesson pages (`lessons/*/index.html`) | Two lines: the name of the bootstrap stylesheet (below), and the provenance region "This page was built from commit `4894c4b`…", which on the local page adds "The checkout had uncommitted changes, so that commit does not hold exactly the files this page was built from" (the five Lean lessons carry the same note once more in their Lean evidence region). With the stylesheet name and that note normalised, every lesson page is byte-identical, including the page of the locally executed lesson | **Documented, provenance-specific**: the region is regenerated on every build from the commit of the run (ADR 014 decision 9); the note is true of the local checkout (the untracked documents of this feature) and absent on CI |
| 9 pages that are not lessons (`index.html`, `about.html`, `contribute.html`, `educators.html`, `evidence.html`, `glossary.html`, `path/index.html`, `rendering-check.html`, `reproduce.html`) | The name of the bootstrap stylesheet only | As the next row |
| `site_libs/bootstrap/bootstrap-<hash>.min.css` (one file on each side, 509,385 bytes each) | The same 192 rules in a different order (no rule added or removed); the name carries the hash of the content | **Render toolchain, cross-machine**: Quarto's Sass compilation orders these rules differently on macOS and Linux. Not seen between runners: the page records of runs of the same byte class on CI are identical (section 5) |
| 32 preview images (`previews/*.png`), 3 figures of `rendering-check` (a page that is not a lesson and is always executed), and the one figure of the locally executed lesson `mechanics/09` | The compressed bytes; **the decoded pixels are identical in all 36 files** (every scanline compared) | **PNG encoder, cross-machine**: the zlib stream of the PNG writer differs between the platforms; no pixel differs, so the figures of the executed lesson and of the rendering check and the previews that the browser captured are the same images |
| `search.json` (347 entries) | The order of the entries; as sets the entries are identical | **Render order, cross-machine**: the order follows the directory listing of the platform |
| `sitemap.xml` (41 locations) | The order of the entries; as sets identical | As above |
| The figures and data files of the 31 inherited lessons (the `index_files/` of every other lesson) | Nothing: byte-identical | Inherited from the base, as designed |


**Every differing file, by path.** The 79 files that differ and the one
file present under a different name, each with its classification (the
rows of the table above). Paths are relative to the root of the site.
The list was recomputed on 2026-10-17 from the retained copies of the
two sites (the `github-pages` artifact 12036343203 as downloaded on
2026-10-16, and `site/_site` of the local run), with the counts above
reproduced: 98 byte-identical, 79 differing, 1 under a different name.
For each lesson page, replacing the stylesheet's name and removing the
note on uncommitted changes leaves the two files byte-identical (all 32);
each PNG decodes to identical image data (all 36); the 347 entries of
`search.json` are equal as a set.

| # | Path in the site | Classification |
|---|---|---|
| 1 | `about.html` | Stylesheet name only (render toolchain, cross-machine) |
| 2 | `contribute.html` | Stylesheet name only (render toolchain, cross-machine) |
| 3 | `educators.html` | Stylesheet name only (render toolchain, cross-machine) |
| 4 | `evidence.html` | Stylesheet name only (render toolchain, cross-machine) |
| 5 | `glossary.html` | Stylesheet name only (render toolchain, cross-machine) |
| 6 | `index.html` | Stylesheet name only (render toolchain, cross-machine) |
| 7 | `lessons/agents-abm/01-particles-in-a-box/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 8 | `lessons/agents-llm/01-an-agent-runs-an-experiment/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 9 | `lessons/agents-llm/02-a-counterexample-hunter/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 10 | `lessons/agents-llm/03-three-reviewers/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 11 | `lessons/agents-llm/04-an-experimental-design-agent/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 12 | `lessons/lean/01-proving-what-the-simulation-showed/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 13 | `lessons/lean/02-momentum-in-a-collision-proved/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 14 | `lessons/lean/03-what-symplectic-euler-conserves/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 15 | `lessons/lean/04-lean-exercises-on-your-machine/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 16 | `lessons/lean/05-the-chirp-law-proved/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 17 | `lessons/mechanics/01-kinematics-as-a-program/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 18 | `lessons/mechanics/02-newtons-laws/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 19 | `lessons/mechanics/03-projectile-motion-with-drag/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 20 | `lessons/mechanics/04-harmonic-oscillator/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 21 | `lessons/mechanics/05-numerical-integrators/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 22 | `lessons/mechanics/06-energy-conservation/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 23 | `lessons/mechanics/07-momentum-and-collisions/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 24 | `lessons/mechanics/08-kepler-orbit/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 25 | `lessons/mechanics/09-verifying-scientific-code/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 26 | `lessons/mechanics/09-verifying-scientific-code/index_files/figure-html/fig-verification-convergence-output-1.png` | PNG encoder, pixels identical (cross-machine) |
| 27 | `lessons/mechanics/10-automated-analysis-pipelines/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 28 | `lessons/mechanics/11-gravitational-wave-strain/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 29 | `lessons/mechanics/12-inverse-physics-parameter-discovery/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 30 | `lessons/mechanics/13-double-pendulum-chaos/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 31 | `lessons/mechanics/14-lagrangian-mechanics/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 32 | `lessons/mechanics/15-hamiltonian-mechanics/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 33 | `lessons/mechanics/16-resonance/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 34 | `lessons/thermodynamics/01-random-walks-and-diffusion/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 35 | `lessons/thermodynamics/02-kinetic-theory-of-gases/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 36 | `lessons/thermodynamics/03-entropy-from-ensembles/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 37 | `lessons/waves/01-the-wave-equation/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 38 | `lessons/waves/02-interference-and-resonance/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 39 | `lessons/waves/03-sound-and-the-doppler-effect/index.html` | Provenance region (documented, provenance-specific) and stylesheet name |
| 40 | `path/index.html` | Stylesheet name only (render toolchain, cross-machine) |
| 41 | `previews/agent-experiment.png` | PNG encoder, pixels identical (cross-machine) |
| 42 | `previews/automated-analysis-pipelines.png` | PNG encoder, pixels identical (cross-machine) |
| 43 | `previews/chirp-law-proved.png` | PNG encoder, pixels identical (cross-machine) |
| 44 | `previews/collision-momentum-proved.png` | PNG encoder, pixels identical (cross-machine) |
| 45 | `previews/counterexample-hunter.png` | PNG encoder, pixels identical (cross-machine) |
| 46 | `previews/double-pendulum-chaos.png` | PNG encoder, pixels identical (cross-machine) |
| 47 | `previews/energy-conservation.png` | PNG encoder, pixels identical (cross-machine) |
| 48 | `previews/entropy-from-ensembles.png` | PNG encoder, pixels identical (cross-machine) |
| 49 | `previews/experimental-design-agent.png` | PNG encoder, pixels identical (cross-machine) |
| 50 | `previews/gravitational-wave-strain.png` | PNG encoder, pixels identical (cross-machine) |
| 51 | `previews/hamiltonian-mechanics.png` | PNG encoder, pixels identical (cross-machine) |
| 52 | `previews/harmonic-oscillator.png` | PNG encoder, pixels identical (cross-machine) |
| 53 | `previews/interference-and-resonance.png` | PNG encoder, pixels identical (cross-machine) |
| 54 | `previews/inverse-physics.png` | PNG encoder, pixels identical (cross-machine) |
| 55 | `previews/kepler-orbit.png` | PNG encoder, pixels identical (cross-machine) |
| 56 | `previews/kinematics.png` | PNG encoder, pixels identical (cross-machine) |
| 57 | `previews/kinetic-theory-of-gases.png` | PNG encoder, pixels identical (cross-machine) |
| 58 | `previews/lagrangian-mechanics.png` | PNG encoder, pixels identical (cross-machine) |
| 59 | `previews/lean-exercises-on-your-machine.png` | PNG encoder, pixels identical (cross-machine) |
| 60 | `previews/momentum-and-collisions.png` | PNG encoder, pixels identical (cross-machine) |
| 61 | `previews/newtons-laws.png` | PNG encoder, pixels identical (cross-machine) |
| 62 | `previews/numerical-integrators.png` | PNG encoder, pixels identical (cross-machine) |
| 63 | `previews/particles-in-a-box.png` | PNG encoder, pixels identical (cross-machine) |
| 64 | `previews/projectile-with-drag.png` | PNG encoder, pixels identical (cross-machine) |
| 65 | `previews/proving-what-the-simulation-showed.png` | PNG encoder, pixels identical (cross-machine) |
| 66 | `previews/random-walks-and-diffusion.png` | PNG encoder, pixels identical (cross-machine) |
| 67 | `previews/resonance.png` | PNG encoder, pixels identical (cross-machine) |
| 68 | `previews/scientific-review.png` | PNG encoder, pixels identical (cross-machine) |
| 69 | `previews/sound-and-the-doppler-effect.png` | PNG encoder, pixels identical (cross-machine) |
| 70 | `previews/symplectic-euler-conserved-energy.png` | PNG encoder, pixels identical (cross-machine) |
| 71 | `previews/verifying-scientific-code.png` | PNG encoder, pixels identical (cross-machine) |
| 72 | `previews/wave-equation.png` | PNG encoder, pixels identical (cross-machine) |
| 73 | `rendering-check.html` | Stylesheet name only (render toolchain, cross-machine) |
| 74 | `rendering-check_files/figure-html/fig-damped-oscillation-output-1.png` | PNG encoder, pixels identical (cross-machine) |
| 75 | `rendering-check_files/figure-html/fig-measured-transmission-output-1.png` | PNG encoder, pixels identical (cross-machine) |
| 76 | `rendering-check_files/figure-html/fig-modelled-transmission-output-1.png` | PNG encoder, pixels identical (cross-machine) |
| 77 | `reproduce.html` | Stylesheet name only (render toolchain, cross-machine) |
| 78 | `search.json` | Order of the entries, identical as a set (render order, cross-machine) |
| 79 | `sitemap.xml` | Order of the entries, identical as a set (render order, cross-machine) |
| 80 | `site_libs/bootstrap/bootstrap-341df6340d57460e6552c0b515ce1e92.min.css` (full, CI) and `site_libs/bootstrap/bootstrap-da74c8c86e4a08e6a40bd57b48342c6b.min.css` (selective, local) | The one file under a different name: the stylesheet row above (render toolchain, cross-machine) |

**Statement.** On this commit the selective verification published the
site the full verification published, up to (a) the documented
provenance region, which names the same commit on both and on the local
build truthfully adds that the checkout was not clean, and (b) three
cross-machine render differences that are not provenance-specific and
not scientific: the order of the stylesheet's rules, the PNG encoder's
bytes with identical pixels, and the order of the search index and the
sitemap. No executed output, figure pixel, number, or page text differs.
This shows that the selective site equals the full site **when the
inherited results are valid**; it does not show that they are valid, which
is what decisions 1 to 3 of ADR 017 establish per lesson and what section
5 shows the environment identity cannot fully establish today.

**The cross-runner uncertainty, reported.** The local render ran on
another machine than the full run, so this comparison includes the
cross-machine differences above; a comparison between two hosted runners
of a selective render does not exist (no run on `main` takes a base). What
section 5 adds from the runs on `main`: two runners of the same byte class
publish byte-identical sites for identical inputs, so the three
cross-machine differences above are a property of the developer's
platform, not of the runners; and two runners of different classes differ
in the executed results of 7 of 32 lessons, which a selective run that
inherits them carries into its site unchanged.

## 2. The fail-closed demonstrations

Each case the Issue names, with the test that demonstrates it (by file and
name; the F61 suites, extended by the prototype of section 3) or the
recorded run. The rule everywhere is the one of ADR 014 decision 4: a
condition that cannot be established executes the lesson, or every lesson,
and the reason is printed and recorded.

| Case | Demonstrated by |
|---|---|
| The base is missing | `tests/integration/test_selection.py::test_no_base_selects_every_lesson`, `::test_a_base_that_cannot_be_used_selects_every_lesson[break_missing]`, `::test_verify_with_a_base_that_is_missing_runs_in_full`, `::test_without_a_base_a_run_with_base_is_a_full_run`; `tests/integration/test_fetch_base.py::test_a_run_without_a_listing_gives_no_base`, `::test_an_empty_listing_gives_no_base`, `::test_a_failing_api_gives_no_base_and_does_not_fail_the_run`; `tests/integration/test_ci_workflow.py::test_a_run_on_main_never_receives_a_base` (today's `main`) |
| The base is expired | `tests/integration/test_fetch_base.py::test_an_artifact_whose_record_does_not_fit_is_rejected[expired-no single unexpired]` (an expired artifact is never downloaded); the age bound of a chain: `tests/integration/test_provenance.py::test_a_result_older_than_the_bound_is_rejected` |
| The base is invalid (a digest that does not match) | The archive: `tests/integration/test_fetch_base.py::test_a_download_that_is_not_the_recorded_archive_is_rejected`; a lesson: `tests/integration/test_selection.py::test_the_selection_names_exactly_the_lessons_whose_digest_differs`, `::test_a_new_lesson_is_executed`; a damaged store entry: `::test_a_base_that_cannot_be_used_selects_every_lesson[break_store_result]`, `[break_store]`, `[break_store_symlink]`; the run that uploaded it: `tests/integration/test_provenance.py::test_a_base_that_names_another_run_than_the_one_that_uploaded_it_is_rejected`; an incomplete or inconsistent provenance record: `::test_a_record_that_does_not_cover_exactly_the_base_s_lessons_is_rejected`, `::test_an_incomplete_or_inconsistent_lesson_entry_is_rejected`, `::test_a_malformed_derivation_link_is_rejected`, `::test_an_inherited_result_that_is_not_the_previous_base_s_is_rejected` |
| The base is stale (an older format) | `tests/integration/test_selection.py::test_a_base_that_cannot_be_used_selects_every_lesson[break_format]`, `[break_identity]`, `[break_lessons]`, `[break_truncated]`; `tests/integration/test_provenance.py::test_a_base_of_another_format_is_rejected`, `::test_the_record_is_written_and_read_back_and_another_format_is_not_read` |
| The base is incompatible: the check identity differs | `tests/integration/test_selection.py::test_a_change_to_the_checks_makes_the_run_a_full_run` (every input of the identity), `::test_no_reused_result_is_certified_by_older_check_logic` (one input of each validity domain), `::test_a_change_to_an_input_no_classification_names_invalidates_every_domain`, `::test_a_full_selection_refuses_the_targeted_run_and_names_the_full_run`. Recorded runs: 38534115654 (pull request #161, 2026-10-14, 22 lessons: "the checks changed since the base (identity differs)", 22 of 22 executed, `build` 17 min 31 s) and 38862000934 (pull request #191, 2026-10-16, 32 lessons: the same reason, 32 of 32 executed, `build` 20 min 44 s, wall clock 28 min 06 s) |
| The base is incompatible: the environment identity differs | `tests/integration/test_provenance.py::test_a_differing_environment_identity_is_rejected` (image, image version, locale, time zone), `::test_a_changed_pin_changes_the_identity` (each pin), `::test_a_missing_pin_is_recorded_and_differs_from_a_present_one`, `::test_a_base_without_an_environment_identity_is_rejected` |
| A shared input changed | `tests/integration/test_selection.py::test_a_changed_shared_input_selects_every_lesson` (the pins, the Lean toolchain and manifest, `src/pbc/authoring`, the shared files of `site/`), `::test_a_changed_module_selects_the_lessons_that_import_it`, `::test_a_module_whose_importers_cannot_be_followed_selects_every_lesson`, `::test_a_lesson_without_a_digest_selects_every_lesson`; `tests/integration/test_lesson_digest.py::test_each_kind_of_input_changes_the_digest`. Recorded: the push runs 38659296393 (after F64 changed shared files of `site/`) and 38868679531 (after F119 changed `uv.lock`) hold no lesson digest equal to the previous base's (section 5) |
| A check implementation changed | The identity rows above; `tests/integration/test_lesson_digest.py::test_each_input_of_the_identity_changes_it`, `::test_a_new_check_file_changes_the_identity` |
| A pull request artifact, or an unverified run, offered as a base | `tests/integration/test_fetch_base.py::test_a_run_that_is_not_a_verified_push_run_on_main_is_rejected` (a pull request run, a fork, another workflow, a failed run), `::test_a_main_run_whose_verify_did_not_succeed_is_rejected`, `::test_a_run_without_the_job_verify_is_rejected`, `::test_an_artifact_whose_record_does_not_fit_is_rejected` (another run's artifact, another branch); `tests/integration/test_provenance.py::test_a_run_that_is_not_a_verified_push_run_on_main_is_rejected`; `tests/integration/test_ci_workflow.py::test_the_base_is_published_by_main_only_after_verify_passed`, `::test_the_candidate_of_the_base_is_made_on_main_only` |
| The chain is too deep | `tests/integration/test_provenance.py::test_a_chain_deeper_than_the_bound_is_rejected`, `::test_a_complete_execution_starts_a_new_chain` |

**The full-run fallback under the approved timeout.** The timeout the
owner approved on F118's record is 60 minutes for the one `build` job of
a full run, for up to 45 lessons (ADR 014, status, 2026-10-15). Recorded
full runs after that decision, at 32 lessons, each a complete execution
under the F119 workflow (three executions per lesson):

| Run | Why it was a full run | `build` job | Wall clock of the run |
|---|---|---|---|
| 38862000934, pull request #191, 2026-10-16 | the base was rejected: the checks changed | 20 min 44 s | 28 min 06 s |
| 38868679531, push to `main`, 2026-10-16 | a run on `main` takes no base | 20 min 50 s | 28 min 01 s |
| 38876222290, push to `main`, 2026-10-16 | a run on `main` takes no base | 25 min 52 s | 34 min 14 s (to the end of `deploy`) |

All three finished under the 60-minute timeout, with 34 to 39 minutes to
spare; the slowest was 5 minutes slower than the fastest on the same
work, which is the runner (section 5), as F118 found.

## 3. The chain's provenance: the format and the prototype

**Specified.** A base of `main` is today `digests.json` (the format, the
check identity, the input digest of every lesson), `pages.json` (the
checksum of every built file with the build commit normalised), and
`freeze/` (the executed results). ADR 017 decisions 2 and 5 add a fourth
file, `provenance.json`, whose format `src/pbc/authoring/provenance.py`
specifies and prototypes (format 1):

- `run`: the run that made the base (its id, commit, event, branch,
  repository, the conclusion of its job `verify`, and when), as the runs
  API records it; the name of an artifact decides nothing.
- `environment`: the execution-environment identity of that run
  (section 5): `enforced` (required equal for reuse: the content of the
  pins `.python-version`, `pyproject.toml`, `uv.lock`,
  `lean/lean-toolchain`, `lean/lake-manifest.json`,
  `.github/actions/prepare/action.yml`, and the runner's image label,
  image version, locale, time zone, and, by the owner's amendment of
  section 10, CPU model and instruction-set flags) with its digest
  `identity`, and `recorded` (carried with every origin for the audit,
  not required equal: the runner version).
- `derived_from`: the base this one inherited from (the run and the
  digest of its provenance record), or null for a complete execution.
  Supersession is explicit: the chain can be walked back to the run that
  executed every lesson.
- `chain`: `depth` (the number of bases since the last complete
  execution) and `start` (the run that began the chain).
- `lessons`: per lesson, `executed` (in this run) and `origin`: the run
  and commit that executed its results, the environment identity of that
  run, what that run recorded of its runner, the depth at which it
  executed, and when.

The published site carries `site_record(provenance)` beside its
checksums: per lesson "executed in this run (R)" or "inherited from run R
at commit C", with the run, commit, environment identity, and depth of
the origin.

**Acceptance** (`accept`): a base is inherited from only when the run that
uploaded it is a `push` run of `ci.yml` on `main` of this repository that
concluded with success and whose job `verify` concluded with success, the
record inside the base names that run and its commit, the record is of
the current format, the base's and this run's environment records are
complete and consistent (the identity is the digest of its components)
and report every enforced runner fact (a fact that is not reported makes
the identity unknown, so two runs that both omit the CPU model are never
equal: F121 has to record it), the enforced environment identity equals
this run's, the record is complete and consistent (an entry with an
origin, a time, and an environment identity equal to the digest of its
components and to the base's identity, for executed and inherited
results alike, for exactly the lessons of the base's `digests.json`; an
executed lesson
names this run, its commit, and its depth, an inherited one an earlier
depth; a chain of depth 0 is a complete execution that starts at this
run and names no `derived_from`; a deeper one names, in `derived_from`,
the run and the digest of the record of the base it was derived from,
continues that record's chain by one, and inherited exactly that
record's origins, so the caller gives that record and a derived base
without it is rejected), the chain's depth stays within the bound, and
no inherited result is older than the bound. The bounds proposed for the owner's approval:
**30 days** (the retention of the artifact, so that a complete execution
is forced at least once per retention period, by event) and **depth 10**.
The expected effect of the depth bound is small: of the 102 merges to
`main` from 2026-10-01 to 2026-10-15, 71 changed an input of the check
identity (`docs/verification-audit.md`), and each of those starts a new
chain under ADR 017 decision 5, so a chain of ten incremental merges is
rare in the measured history; the bound is a ceiling, not the expected
depth.

**Derivation** (`derive`): the record of the base this run leaves. An
inherited lesson keeps the origin it had; an executed lesson gets this run
as its origin; a run that reused nothing (a complete execution, or a
selection that was a full run) starts a chain of depth 0 and names no
`derived_from`.

**Prototyped with tests** (`tests/integration/test_provenance.py`):

- rejected as a base: a pull request run, a manually dispatched run, a run
  on another branch, a fork, another repository, another workflow, a
  failed run, a run with no result, a run whose `verify` failed or did not
  run (`test_a_run_that_is_not_a_verified_push_run_on_main_is_rejected`);
  a record that names another run than the one that uploaded it; a record
  of another format or an incomplete one
  (`test_a_base_of_another_format_is_rejected`); a record that does not
  give the origin of exactly the base's lessons (empty, partial, or
  short of a lesson of the base:
  `test_a_record_that_does_not_cover_exactly_the_base_s_lessons_is_rejected`),
  an incomplete or inconsistent lesson entry
  (`test_an_incomplete_or_inconsistent_lesson_entry_is_rejected`), a
  complete execution with an inconsistent chain
  (`test_a_complete_execution_with_an_inconsistent_chain_is_rejected`), a
  derived base checked without, or against another than, the base it was
  derived from
  (`test_a_derived_base_is_accepted_only_against_the_base_it_was_derived_from`),
  a malformed derivation link
  (`test_a_malformed_derivation_link_is_rejected`), and an inherited
  result that is not the previous base's
  (`test_an_inherited_result_that_is_not_the_previous_base_s_is_rejected`);
  a differing or missing
  environment identity (section 2); a chain deeper than the bound; a
  result older than the bound;
- an inherited result keeps its origin through a chain of three
  incremental bases after a complete one
  (`test_an_inherited_result_keeps_its_origin_through_a_chain_of_three_bases`):
  the lesson executed by run 1 alone still names run 1, its commit, its
  environment identity, and depth 0 in the fourth base, while the base of
  run 4 has depth 3 and names run 3 as what it derived from, and the
  chain walks back 4, 3, 2, 1;
- a complete execution resets the chain
  (`test_a_complete_execution_starts_a_new_chain`); a reused lesson
  without an origin cannot be inherited
  (`test_a_reused_lesson_without_an_origin_cannot_be_inherited`);
- the site record names the origin of every lesson
  (`test_the_site_record_names_the_origin_of_every_lesson`); the record is
  written, read back, and not read in another format; the module describes
  a base as a command on the pinned Python.

Nothing calls the module: `scripts/collect-base.sh`, `scripts/fetch-base.sh`,
`pbc.authoring.selection`, and `ci.yml` are unchanged. F121 would write
`provenance.json` in `collect-base.sh`, check it in `fetch-base.sh` with
the environment identity read on the runner, and copy the site record into
the built site, if the owner accepts ADR 017.

## 4. One production build

`deploy` publishes exactly the artifact CI verified and builds nothing.
The tests (F58 and F61):

- `tests/integration/test_ci_workflow.py::test_deploy_job_publishes_the_verified_artifact_and_builds_nothing`:
  the job runs only on a push to `main` after the required check, has one
  step, `actions/deploy-pages`, with no checkout and no command.
- `tests/integration/test_ci_workflow.py::test_the_site_is_built_in_one_job_and_uploaded_with_its_record`:
  one job builds the site and uploads it as `github-pages` with the record
  of its files.
- `tests/integration/test_ci_workflow.py::test_a_job_that_checks_the_built_site_checks_the_one_that_was_built`:
  every job that checks the site downloads that artifact and compares it
  with the record before it checks anything.
- `tests/integration/test_ci_scripts.py::test_a_job_gets_the_site_that_was_built`,
  `::test_what_a_job_had_before_is_replaced`,
  `::test_a_site_that_is_not_the_built_one_stops_the_job`,
  `::test_an_incomplete_hand_over_stops_the_job`,
  `::test_an_empty_list_of_checksums_stops_the_job`: the hand-over script
  (`scripts/fetch-built-site.sh`) accepts only the site whose every file
  matches the record.
- `tests/integration/test_ci_workflow.py::test_the_base_is_published_by_main_only_after_verify_passed`
  and `::test_the_candidate_of_the_base_is_made_on_main_only`: the base
  follows the same rule as the site; nothing is republished before
  `verify` passed.

Under ADR 017 this does not change: the `build` job of a push to `main`
would render every page from the store and the current tree, check the
site, and upload it; `deploy` would publish that artifact.

## 5. The environment identity

### What the hosted runners varied across the named runs

Read from the "Set up job" section of the `build` job's log of each run
(the logs of 2026-10-14 and 2026-10-15 named by ADR 017 and F118, and the
runs of 2026-10-16):

| Run | Date | Runner version | Image | Image version | Provisioner version |
|---|---|---|---|---|---|
| 38527223459 (`main`) | 2026-10-14 | 2.337.0 | ubuntu-24.04 | 20261004.327.1 | 20261002.596 |
| 38534115654 (pull request #161, full run) | 2026-10-14 | 2.337.0 | ubuntu-24.04 | 20261004.327.1 | 20261002.596 |
| 38545077253 (`main`) | 2026-10-14 | 2.337.0 | ubuntu-24.04 | 20261004.327.1 | 20261002.596 |
| 38607388478, 38621916706, 38639021950 (`main`) | 2026-10-14 | 2.337.0 | ubuntu-24.04 | 20261004.327.1 | 20261002.596 |
| 38659296393 (`main`) | 2026-10-15 | 2.337.0 | ubuntu-24.04 | 20261004.327.1 | 20261002.596 |
| 38687330455 (`main`) | 2026-10-15 | 2.337.0 | ubuntu-24.04 | 20261012.334.1 | 20261012.601 |
| 38868679531, 38876222290 (`main`) | 2026-10-16 | 2.337.0 | ubuntu-24.04 | 20261012.334.1 | 20261012.601 |

The image version changed once in the period (between 2026-10-15 00:18
and 05:32 UTC); the runner version did not. The logs record **no CPU
model, no CPU flags, no locale, and no time zone**: nothing in the
workflow prints them, and the runner's setup does not. The versions the
pins fix and the logs confirm: Python 3.14 (`.python-version`), the
locked packages including `quarto-cli` 1.10.19 and Playwright with its
browser build (`uv.lock`), Lean and Mathlib (`lean/lean-toolchain`,
`lean/lake-manifest.json`), elan v4.2.4 by checksum
(`.github/actions/prepare/action.yml`). **uv itself is not pinned**: the
action installs the version it resolves (0.13.1 in the runs of
2026-10-14 and 2026-10-16), and the lock file, not uv's version, fixes
the packages.

### The byte comparison across runners for identical inputs

The sources are the `verification-base` artifacts of the push runs on
`main` (each a complete execution; retained 30 days), downloaded on
2026-10-16 and compared where the lesson digests are equal: eleven runs
from 38607388478 (2026-10-14) to 38868679531 (2026-10-16), in three
groups whose lesson digests are equal within the group and differ between
groups (F68 and F70 added lessons; F64 and F119 changed shared inputs):

- group A: 38607388478 (28 lessons), 38621916706, 38633313992,
  38639021950 (32 lessons); all on image version 20261004.327.1;
- group B: 38687330455, 38745333873, 38789966932, 38795229814,
  38809123210 (32 lessons); all on image version 20261012.334.1;
- group C: 38868679531 alone (38876222290 is its successor with equal
  digests; its base was downloaded for section 1).

Sixteen pairs of runs, 95 or 105 stored files per pair (the
`execute-results/html.json` of every lesson and its figure and data
files). The result:

- **Every stored result differs between any two runs in the cell
  identifiers only** (`::: {#2fd31d3e .cell ...}`), which the Jupyter
  engine draws anew on each execution. They do not reach the built page
  (the HTML has `<div class="cell">` without them), the determinism check
  compares the pages and passes, and `pages.json` shows no difference
  from them. A documented, provenance-neutral difference of the store.
- **The runs fall into exactly two byte classes**, in group A and in
  group B alike, by every differing file at once. Within a class, every
  stored file of every lesson is byte-identical (cell identifiers aside).
  Across the classes, **10 stored files of 7 of the 32 lessons differ**,
  identically for every cross-class pair:
  `agents-abm/01-particles-in-a-box` (the result and two figures),
  `lean/01-proving-what-the-simulation-showed` (one figure),
  `lean/02-momentum-in-a-collision-proved` (one figure),
  `mechanics/04-harmonic-oscillator` (one figure),
  `mechanics/11-gravitational-wave-strain` (`chirp-masses.json`),
  `thermodynamics/02-kinetic-theory-of-gases` (the result and one figure),
  `waves/01-the-wave-equation` (one figure). The page records agree: the
  built sites of two runs of different classes differ in those **10
  lesson files, 3 preview images derived from them, and `search.json`:
  14 of 178 files**; two runs of the same class publish byte-identical
  sites (the commit normalised).
- **What differs is not only a last digit.** `chirp-masses.json` differs
  in the fifth decimal of 5 values (a rounding boundary);
  `fig-convergence-output-1.png` in 9 bytes of 2 scanlines and
  `fig-oscillator-energy-growth-output-1.png` in 101 bytes of 19
  scanlines (a tick label or an anti-aliased edge); but
  `fig-speeds-output-1.png` of the gas lesson is 1111 pixels wide in one
  class and 1090 in the other, and the two results that differ are
  stochastic simulations whose seeded trajectories diverge under a
  different floating-point path: the gas lesson's moment ratio is 1.986
  in one class and 1.946 in the other, "within 0.6 standard errors of
  two" against "within 3.9", and the kinetic-theory lesson's wrong-curve
  check "fails at 5 of the five points" against "3 of the five". The
  page text that states a numerical conclusion differs between the
  classes.
- The byte class is not the speed class of F118: runs 38607388478 and
  38621916706 are both "slow" there and are of different byte classes
  here. It is not the image version: group A has both classes on one
  image version. What distinguishes the classes is not in the logs; the
  CPU model, which the hosted runners vary and which the digest cannot
  see, is the one candidate ADR 017 decision 3 names, and it is unshown
  because unrecorded.
- **How often a merge crosses the class boundary.** In the order of the
  runs, 4 of the 7 consecutive pairs within a group changed class
  (A: 1 of 3; B: 3 of 4). On that sample, an inherited result would come
  from the other class about half the time, and a mitigation that
  requires the CPU model equal would make about half of the incremental
  merges complete executions.

### The classification into enforceable, recorded, and residual

| Item of ADR 017 decision 3 | Classification | Evidence and value |
|---|---|---|
| Runner image label (`ubuntu-24.04`) | **Enforceable**: required equal | In the workflow and the logs; unchanged in the period |
| Runner image version | **Enforceable**: required equal (proposed); effect on bytes not shown either way | Changed once in the period (20261004.327.1 to 20261012.334.1); the groups of equal digests do not straddle the change, so no pair isolates its effect. Requiring it equal forces a complete execution at each image update (about weekly), an event-driven audit at no new mechanism |
| Python, uv, Quarto, Lean, Mathlib, the browser build, the preparation | **Enforceable**: by the content of the pins (six files) in the identity; a change to any of them already changes every lesson digest (shared inputs) and the check identity | `test_a_changed_pin_changes_the_identity`; uv's own version is the one gap: not pinned, resolved by the action (0.13.1 in both measured runs); F121 should pin it (`uv-version` of the action, or `required-version` in `pyproject.toml`) |
| Fonts and system libraries the render depends on | **Enforceable through the image version** as far as the image provides them; the figures use the fonts bundled with matplotlib, and the HTML render uses none | No difference attributable to them was seen within a byte class |
| Locale and time zone | **Enforceable**: required equal, read on the runner (`locale`, `date +%Z`) and recorded in the identity | Not in the logs today; the image's defaults are `C.UTF-8` and UTC; F121 reads and records them |
| CPU model and flags | **Residual today, recordable by F121**: not in the logs, not pinned by anything, and shown to change bytes of 7 of 32 lessons | The two byte classes above. Options for the owner: (a) record only, and accept that an inherited page may show the other class's bytes (verified when executed, reproducible on that class); (b) require equal, which halves the benefit on the measured sequence |
| The chain's acceptance (an error propagates) | **Enforceable**: the run record, the format, the derivation link, the depth and age bounds | Section 3 |

**The residual risk, quantified on the measured runs.** Under ADR 017
with the environment identity of the enforceable rows and the CPU model
recorded only, a page inherited across a class boundary shows the bytes
the other class computed: on this sample 7 of 32 lessons (22 percent), 14
of 178 files of the site, on about half of the incremental merges. For
five of those seven lessons the difference is a last digit or a pixel;
for two, both stochastic simulations, the stated numerical conclusion
differs. Today the same two classes alternate on `main` from one push to
the next, so the published site already changes its bytes between
classes without any change of inputs; what ADR 017 changes is that one
site could mix results of both classes, and that a lesson's page and its
reproduction were checked on the class that executed it, not on the
class that rendered the page.

**A check that recomputes on the checking machine.** One built-site
check, `tests/e2e/test_comparator.py::test_the_embedded_series_and_metrics_agree_with_a_fresh_run_of_pbc`,
is not in the same-machine group: it recomputes the gravitational-wave
lesson's model series with the code of `src/pbc` on the machine that
checks the site and compares them with the data embedded in the page at
6e-6. With inherited data (computed on a runner) checked on the
developer's machine it failed in the run of section 1 (25 of 14,748
values beyond the tolerance, the worst by 3.2e-5). On CI the `e2e` jobs
already run on other runners than `build`, so the check already compares
across runners on every pull request with a base and has passed in the
measured ones; under ADR 017 the inherited data of `main` would be
compared the same way. Whether the cross-class differences of the hosted
runners stay within that tolerance is not shown by the runs (the
embedded series of `chirp-masses.json` differed in 5 values at the fifth
decimal across the classes, section 5); a check of this kind either
tolerates the measured cross-class spread or belongs to the same-machine
group, which F121 decides with the evidence here.

## 6. The costs

Measured from the Actions API (job start to job end; wall clock from the
creation of the run to its end), with the F61 and F118 measurements of
`docs/release-readiness.md`.

**The one-lesson pull request, measured.** The first one-lesson pull
request after F119 (run 38874606240, pull request #195, 2026-10-16, 32
lessons, "selective run against base 6518cf5c3da4: 1 of 32 lessons
executed, 31 restored", every cache of the preparation hit):

| Measure | Duration |
|---|---|
| Wall clock | 14 min 05 s |
| Critical path: `build` (7 min 15 s), then `e2e (other)` (6 min 35 s), then `verify` | 13 min 55 s |
| `build`: prepare 1 min 56 s; group `build` 5 min 02 s = `lean-build` 25 s, `site-build` 1 min 52 s, `determinism` 1 min 43 s, the reproduction of one lesson 43 s | 7 min 15 s |
| The longest fixed job beside `build`: `integration-other` | 6 min 30 s |
| Against ADR 015: the 20-minute budget met by 5 min 55 s; the 15-minute target met by 55 s | |

The three one-lesson pull requests of F61 at 22 lessons took 13 min 50 s
to 14 min 43 s (2026-10-14, before F119). The fixed cost of a run is the
runner preparation (about 100 s in each of nine jobs), the Lean build
(19 to 25 s), the three `integration` parts (5 to 6.5 minutes side by
side), `e2e (other)` (6.5 to 7 minutes), and the Quarto start of two
builds; the lesson-dependent cost is about 4 s of `build` per restored
lesson (F118) and 40 to 60 s for the executed lesson.

**The one-lesson merge under incremental `main`, a projection.** A push
to `main` that merges a one-lesson pull request would run the same
selection against the previous base of `main` (ADR 017 decision 1), plus
the collection and publication of the base and the provenance record
(`base` took 8 to 9 s in today's runs) and `deploy` (10 s to 1 min 09 s).
Projected from run 38874606240: **about 14 to 15 minutes of wall clock
and about 45 minutes of runner time**, against the measured full runs on
`main` of the same day (28 min 01 s and 34 min 14 s of wall clock; `build`
alone 20 min 50 s and 25 min 52 s). A projection, not a measurement: no
run on `main` has taken a base.

**The full-run fallback, measured and projected.** Measured at 32 lessons
under the F119 workflow: the group `build` costs 39 to 46 s per lesson
(20 min 47 s and 24 min 32 s for 32 lessons; the spread is the runner),
with the reproduction 45 to 51 percent of it. Projections at the measured
bounds, with the preparation at 2 minutes, **labelled projections**:

| Lessons | `build` job, fast bound (39 s per lesson) | slow bound (46 s per lesson) | Against the 60-minute timeout |
|---|---|---|---|
| 32 (measured: 20 min 50 s and 25 min 52 s) | 23 min | 27 min | within |
| 45 (the count the timeout is approved for) | 31 min | 37 min | within |
| 64 | 44 min | 51 min | within at both bounds, 9 minutes of margin at the slow one |
| 110 (the curriculum) | 73 min | 86 min | beyond at both bounds |

F118's bounds (36 to 60 s per lesson, four executions) gave 30 to 49
minutes at 47 lessons; the measured cost after F119 (three executions)
is within them. At 110 lessons the exceptional full run of ADR 017
decision 6 would not fit one job under 60 minutes on these bounds: the
owner's decision between a wider timeout at that count and the lesson
shards of F113 is not forced by F120 (the count is 32) and is restated,
as decision 6 says, when the count grows.

## 7. What is not shown

- That inherited results are valid for the current commit: sections 2
  and 3 show that invalidity the digest, the check identity, and the
  environment identity can see is caught; section 5 shows that the CPU
  class is not seen today.
- The effect of the image version on bytes, in either direction.
- What distinguishes the two byte classes: the CPU model is the
  candidate, not a recorded fact.
- A chain of bases on `main` in CI: the prototype runs in tests only.
- The cross-machine equality of a render: section 1 compares a site
  rendered on a developer's machine with one rendered on a runner, which
  is the comparison the Issue asked for; it is not a comparison between
  two runners.
- The duration of a full run at 45 or 110 lessons, and the retrieval of
  the base by a pull request from a fork (F61, still unmeasured).
- That the prototype validates every field it records: `accept()` checks
  the enforced identity of an origin and its environment digest, but not
  its `recorded` runner facts (the runner version). A known limitation of
  the prototype, found by the last review of F120 and left as it is,
  because the prototype is research work that nothing calls and the
  incremental `main` it serves stays paused; F121 would have to validate
  them before any use.

## 8. The scheduled audit (question 11), as ADR 017 states it

Presented without a recommendation. The defect a scheduled complete
execution detects is exactly what no event-driven check can: an input
the digest does not follow, and environment drift the identity does not
capture (section 5 shows one such drift, the CPU class, and quantifies
it). Its cost is one complete execution per period: today 28 to 34
minutes of wall clock and about 55 minutes of runner time at 32 lessons,
growing with the count as in section 6. Its residual risk is the interval
between executions. Under ADR 017 decision 5 with the proposed bounds, a
complete execution happens at least once per 30 days by event, at every
change of a shared input, of the checks, of the pins, and of the image
version; in the measured fortnight that was 71 of 102 merges.

## 9. The proposal for Issue #150 (question 12)

If the owner accepts ADR 017: close Issue #150 with a comment that names
ADR 017 and the decision; keep the branch
`feature/150-bounded-full-verification-same` and the closed pull request
#175 as the inspectable record; merge, restart, and duplicate nothing of
it (ADR 017 decision 9). If the owner rejects ADR 017: Issue #150 stays
open for the owner's decision between resuming F113 and the raised
timeout of question 10 as the standing gate. The proposal is posted on
Issue #150 by F120.

## 10. The owner's decision of 2026-10-16

The owner decided to **amend, not yet accept**. The amendments, which replace
the mitigations proposed above where they differ, are recorded in the status
of [ADR 017](decisions/017-incremental-main-from-a-chain-of-verified-bases.md):
the CPU model and the relevant instruction-set flags join the enforced
environment identity (amendment 1), and incremental `main` is not activated
until evidence shows that the enforced identity separates the two observed
byte classes (amendment 2). The chain limits stay at 30 days and depth 10,
and the weekly audit is required while the full-run capacity permits.

