# Deployment

The site is static files on GitHub Pages. There is one environment,
`github-pages`, and no staging: the built site of every pull request is
attached to its workflow run for review before merge.

- Public address: <https://taspinar.github.io/physics-by-construction/>
- Configured in one place: `website.site-url` in `site/_quarto.yml`. Pages
  link to each other with relative URLs, so a custom domain later is a change
  of that one value plus the Pages setting.

## How a change is published

```text
pull request -> CI jobs, check verify -> merge to main -> CI jobs on main
             -> site artifact -> check verify -> deploy job -> GitHub Pages
```

1. The jobs of `.github/workflows/ci.yml` each run a group of the checks
   through `./scripts/verify.sh --all --only <group>`, on every pull request
   and on every push to `main` (ADR 012). The `build` job builds the site
   once and uploads `site/_site/` as the `github-pages` artifact, with a
   list of the checksum of every file. The jobs that check the site download
   that artifact and compare it with the list before they check anything.
   The site is also uploaded when the build failed after it wrote a site, so
   that it can be inspected; the job still fails.
2. The job `verify` is the one required check. It passes only when every
   other job succeeded: a job that failed, was cancelled, or was skipped
   fails it.
3. On a push to `main`, and only when `verify` passed, the `deploy` job
   publishes exactly that artifact. It builds nothing and checks out
   nothing, so the published bytes are the verified bytes.
4. The workflow is read-only (`contents: read`). Only the deploy job has
   `pages: write` and `id-token: write`, and it authenticates with the
   short-lived token GitHub issues to the run. No secret is stored or
   referenced. The jobs `build` and `e2e` have one more scope, `actions: read`,
   so that a pull request run can read the runs and artifacts of earlier runs
   to find the base of step 5; no job has any other write permission.
5. **The base of a pull request** (ADR 014 decision 2). On a push to `main`
   the `build` job runs every lesson, collects what it stored (the executed
   results, the digest of every lesson, and the checksum of every page,
   `scripts/collect-base.sh`) and uploads it as `verification-base-candidate`
   for one day. The job `base` runs after `verify` passed, only on `main`,
   and republishes it as the artifact `verification-base` for 30 days. A pull
   request run (`scripts/fetch-base.sh`) takes the base from the latest run
   of `ci.yml` that the runs API records as a `push` run on `main` of this
   repository that completed with success, whose job `verify` concluded with
   success, and that holds exactly one unexpired artifact of that name whose
   recorded digest is the digest of the download. The record names the
   branch only by its short name, which a tag push fills with the tag's
   name, so the full ref is established from the repository and from the
   run itself: the commit of the run must be on the history of
   `refs/heads/main` (the compare API), no tag `refs/tags/main` may exist,
   and the base must hold `provenance.json`, which `collect-base.sh` writes
   from the run's own `GITHUB_REF`, naming `refs/heads/main`, that commit,
   and that run. The record is trusted because the commit is on `main`, so
   the `ci.yml` that wrote it is the reviewed one; a tag push of a commit on
   `main`, even one whose tag is deleted later, is rejected, and so is a base
   without the record. The name of an artifact, its recency, and its
   contents never make a base acceptable; an artifact of
   a pull request run, a fork, or a failed run is not accepted, and a pull
   request cannot upload one (the job `base` does not run for it). The archive is
   unpacked only when it holds plain relative paths, no link, and the three
   parts of a base; nothing in it is executed or read as configuration. The
   `e2e` jobs take the very base the `build` job took, by its run number, and
   check it again. A base that is missing, rejected, damaged, or of another
   format gives a full run, never a failed one. A run on `main` is never
   given a base.

Deployment is automatic for every verified commit on `main`. Nobody deploys by
hand, and nothing deploys from a branch.

## Repository settings

These settings live in GitHub, not in the repository, and only the repository
owner can apply them. Changing any of them needs the owner's explicit
approval.

| Setting | Where | Required value |
|---|---|---|
| Pages source | Settings → Pages → Build and deployment | GitHub Actions |
| Required status check | Settings → Rules → Rulesets → ruleset for `main` | `verify`, together with "Require a pull request before merging", "Block force pushes", and "Restrict deletions" |
| Default workflow permissions | Settings → Actions → General | Read repository contents |
| Dependabot alerts and security updates | Settings → Advanced Security | Enabled |
| Secret scanning and push protection | Settings → Advanced Security | Enabled |

Add the required check only after the `verify` job has run once on a pull
request, so that GitHub knows the check. Enable Pages before the first merge
to `main` that contains the deploy job, or that deployment fails.

## Rollback

See `docs/operations.md`.
