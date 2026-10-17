# Plan: a statistically justified pressure check for agents-abm/01 (Issue #206)

Source: Issue #206 (the authority on scope and acceptance). Out of scope:
ADR 017, F120, F121, the CI workflow, `verify.conf`, the verification
machinery, and every lesson other than `agents-abm/01`.

## Cause (measured at b4baed1, this machine)

Survey of the default gas (`pbc.abm.gas.measure`, 200 discs, dt = 2 ms)
over 240 seeds; the scripts are not part of the repository.

- **Estimator.** P/P_ideal of one run is the wall impulse over the 3.5 s
  measurement divided by N k_B T / A of the same run, on the free square.
  Distribution over runs: mean 1.0542, sd 0.0089, standard error of the
  mean 0.0006; nearly Gaussian (skewness 0.13, excess kurtosis 0.07,
  Shapiro p = 0.93).
- **Expectation.** The page compares with 1 + 2 phi = 1.0633. The model's
  own mean is 0.0091 +- 0.0006 below it, about one run's sd. The offset is
  systematic: 1.0612 +- 0.0009 at dt = 1 ms (100 seeds), 1.0596 +- 0.0012
  at 0.5 ms (60 seeds), so about 0.007 of it is the time step (collisions
  placed late); the omitted third virial term (+3.128 phi^2 = +0.003) and
  the walls of a small box (bulk density about 0.16 % below N/A, about
  -0.002) are each a few thousandths.
- **Uncertainty.** The standard error comes from six runs (t with five
  degrees of freedom); the old test required |mean - 1.0633| < 3 SE with
  no allowance for the offset. Non-centrality 2.5: the probability of
  failure per independent sample is 0.41 (non-central t), 16 of 40
  disjoint groups of six runs failed, resampling gives 0.42.
- **Sampling.** Fixed seeds make a run reproducible on one machine, but
  the dynamics are chaotic: floating-point differences between runner
  classes give, in effect, a new sample (F120). A check is therefore only
  reproducible in its verdict if its false-failure probability over
  samples is small, which the old one's was not.
- **Correlation.** Runs are independent; snapshots in a run are not. The
  20 ms wall impulses of one run are slightly anti-correlated (lag 1 to 10:
  -0.02 to -0.04), and a naive within-run error overstates the spread
  between runs (2.3 % against 0.84 %), so the error must come from the
  spread between runs, as the page already does.

## Acceptance rule (pre-stated)

K = 12 independent seeds (0 to 11 on the page, 12 to 23 for the second
block of the tests). For each quantity, the mean m and standard error e of
the K run values; the check passes iff |m - theory| <= delta + t e, with
t = t_{K-1}(1 - alpha/2), alpha = 0.001 (t = 4.44), and delta the stated
conservative model allowance (not a proved bound; its parts are estimates): 0.015 for P/P_ideal (time step, truncated series, walls:
about 0.012 by the budget above, rounded up), and 2 / (N + 1) = 0.010 for
the moment ratio (a gas of N discs at fixed energy has the ratio
2 N / (N + 1), not two; measured 1.9868 +- 0.0037 over 200 seeds; without
the allowance the ratio check would fail a correct model in about five
samples in a thousand, above alpha). If
the model's true mean is within delta of the theory, the probability of a
false failure is at most alpha (Gaussian run values). The ideal gas law is
rejected iff m - 1 > delta + t e (false pass of an ideal model at most
alpha / 2). Over the 240 surveyed runs (20 disjoint groups of 12) every
group passes, with a margin of at least 0.008 (agreement) and 0.022
(rejection of the ideal law).

## Steps

1. `pbc.abm.acceptance`: the rule as one function used by the page and
   the tests.
2. Experiment: twelve seeds, the rule in the kinetic-theory table, numbers
   for the allowance, the t value and alpha.
3. Lesson text: the tolerance section, the claim, the limits, the
   solution of the self-check, in agreement with the rule.
4. Tests: deterministic invariants in `tests/unit/test_gas.py` (plus the
   exact pressure of one disc between walls); statistical checks in
   `tests/unit/test_particles_in_a_box_experiment.py` on the page's sample
   and on an independent second block; a regression test of the rule on
   synthetic samples with the measured offset and spread (old rule fails
   often, new rule at most alpha at the boundary).
5. `thermodynamics/02`: check the mechanism, record the result (no change
   unless it has the same mechanism).
6. Targeted verification; record the cost.

## Findings during the work

- **thermodynamics/02** (same 240 runs): the offsets of its quantities
  from theory are at most 0.27 run sd (fractions below the quantiles:
  -0.13, -0.25, -0.24, -0.07, +0.13 sd; mean speed +0.27 sd), against
  1.03 sd for the pressure here. It does not have this failure mechanism,
  so it is not changed (Issue scope). Its own risk is the heavy tail of t
  with five degrees of freedom over five comparisons: resampling groups of
  six runs, `largest-distance >= 4` fails in about 6 % of samples (0 of 40
  disjoint groups failed; the largest distance was 3.5). Reported to the
  owner as a candidate follow-up, not fixed here.
- **Cross-references.** `thermodynamics/01`, `02` and `03` cite "the
  tolerance of the gas lesson: four standard errors". They are out of
  scope; the gas lesson keeps describing that simpler tolerance (and when
  it suffices) so their citation stays true.
- **Cost.** The experiment now makes twelve measured and twelve relaxation
  runs instead of six: the lesson's unit tests take about 28 s instead of
  13 s on this machine (the entry point about 14 s instead of 9 s, an
  independent second block about 10 s, the synthetic regression under
  1 s).
