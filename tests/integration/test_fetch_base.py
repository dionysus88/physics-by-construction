"""Which base a pull request run accepts (ADR 014 decision 2).

``fetch-base.sh`` runs here against a fake ``gh`` that answers the runs API
from files, so every case of provenance is one record: the run that produced
an artifact decides, never the artifact's name, its recency, or its contents.
"""

import hashlib
import json
import os
import stat
import subprocess
import zipfile
from pathlib import Path

import pytest
from support.checks import output
from support.paths import SCRIPTS

REPO = "owner/repo"
RUN = 1000
ARTIFACT = 77

FAKE_GH = """#!/usr/bin/env bash
# api [-H header] <path>: answers from $FAKE_API, one file per path (the query
# string is dropped, so the script's own checks do the filtering).
# auth status: the login of a developer's machine, as FAKE_AUTH_EXIT says.
# repo view: the repository of the clone, FAKE_REPO, or none.
case "$1" in
  auth) exit "${FAKE_AUTH_EXIT:-0}" ;;
  repo) [[ -n "${FAKE_REPO:-}" ]] || exit 1; printf '%s\\n' "$FAKE_REPO"; exit 0 ;;
  api) ;;
  *) exit 64 ;;
esac
shift
path=""
while [[ $# -gt 0 ]]; do
  case "$1" in
  -H) shift 2 ;;
  *) path="$1"; shift ;;
  esac
done
path="${path%%\\?*}"
file="$FAKE_API/$(printf '%s' "$path" | tr -c 'A-Za-z0-9\\n' '_')"
[[ -f "$file" ]] || { echo "gh: HTTP 404: $path" >&2; exit 1; }
cat "$file"
"""


def key(path: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in path)


class Api:
    """The state of the fake GitHub, and a run of the script against it."""

    def __init__(self, tmp: Path) -> None:
        self.tmp = tmp
        self.api = tmp / "api"
        self.api.mkdir()
        self.bin = tmp / "bin"
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text(FAKE_GH)
        gh.chmod(gh.stat().st_mode | stat.S_IXUSR)
        self.target = tmp / "work" / "base"
        self.github_output = tmp / "github-output"
        self.add_run(RUN)

    def put(self, path: str, data: object) -> None:
        (self.api / key(path)).write_text(json.dumps(data))

    def put_bytes(self, path: str, data: bytes) -> None:
        (self.api / key(path)).write_bytes(data)

    def add_run(
        self, run: int, *, listed: bool = True, verify: str = "success", **record
    ) -> None:
        data = {
            "id": run,
            "event": "push",
            "head_branch": "main",
            "status": "completed",
            "conclusion": "success",
            "path": ".github/workflows/ci.yml",
            "head_repository": {"full_name": REPO},
            "repository": {"full_name": REPO},
        } | record
        self.put(f"repos/{REPO}/actions/runs/{run}", data)
        self.put(
            f"repos/{REPO}/actions/runs/{run}/jobs",
            {
                "jobs": [
                    {"name": "build", "status": "completed", "conclusion": "success"},
                    {"name": "verify", "status": "completed", "conclusion": verify},
                ]
            },
        )
        if listed:
            path = f"repos/{REPO}/actions/workflows/ci.yml/runs"
            listing = self.read(path) or {"workflow_runs": []}
            listing["workflow_runs"].append({"id": run})
            self.put(path, listing)
        self.add_artifact(run, ARTIFACT + run)

    def read(self, path: str):
        file = self.api / key(path)
        return json.loads(file.read_text()) if file.exists() else None

    def add_artifact(
        self,
        run: int,
        artifact: int,
        entries: dict[str, bytes | None] | None = None,
        **record,
    ) -> None:
        archive = self.tmp / f"base-{artifact}.zip"
        files = entries if entries is not None else good_entries()
        with zipfile.ZipFile(archive, "w") as zipped:
            for name, content in files.items():
                zipped.writestr(name, content if content is not None else b"")
        data = archive.read_bytes()
        digest = "sha256:" + hashlib.sha256(data).hexdigest()
        self.put_bytes(f"repos/{REPO}/actions/artifacts/{artifact}/zip", data)
        found = {
            "id": artifact,
            "name": "verification-base",
            "expired": False,
            "size_in_bytes": len(data),
            "digest": digest,
            "workflow_run": {"id": run, "head_branch": "main"},
        } | record
        path = f"repos/{REPO}/actions/runs/{run}/artifacts"
        listing = self.read(path) or {"artifacts": []}
        listing["artifacts"].append(found)
        self.put(path, listing)

    def fetch(
        self, *arguments: str, without: tuple[str, ...] = (), **extra: str
    ) -> subprocess.CompletedProcess[str]:
        """Run the script as CI does, or without the variables ``without``
        and with the variables ``extra``, as a developer's machine has it."""
        env = {
            **os.environ,
            "PATH": f"{self.bin}:{os.environ['PATH']}",
            "FAKE_API": str(self.api),
            "GH_TOKEN": "token",
            "GITHUB_REPOSITORY": REPO,
            "GITHUB_OUTPUT": str(self.github_output),
            **extra,
        }
        for name in without:
            env.pop(name, None)
        return subprocess.run(
            [SCRIPTS / "fetch-base.sh", *arguments, str(self.target)],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def outputs(self) -> dict[str, str]:
        lines = self.github_output.read_text().splitlines()
        return dict(line.split("=", 1) for line in lines)


def good_entries() -> dict[str, bytes | None]:
    return {
        "digests.json": json.dumps({"format": 1, "lessons": {}}).encode(),
        "pages.json": json.dumps({"format": 1, "files": {}}).encode(),
        "freeze/lessons/a/index/execute-results/html.json": b"{}",
    }


@pytest.fixture
def api(tmp_path: Path) -> Api:
    return Api(tmp_path)


def assert_no_base(api: Api, result: subprocess.CompletedProcess[str], why: str):
    # Not an error: the run goes on and executes every lesson.
    assert result.returncode == 0, output(result)
    assert "No base:" in result.stdout, output(result)
    assert why in result.stderr + result.stdout, output(result)
    assert not api.target.exists()
    assert api.outputs() == {"accepted": "false", "run-id": ""}


def test_the_base_of_a_verified_push_run_on_main_is_accepted(api: Api):
    result = api.fetch()
    assert result.returncode == 0, output(result)
    assert api.outputs() == {"accepted": "true", "run-id": str(RUN)}
    assert (api.target / "digests.json").is_file()
    assert (api.target / "pages.json").is_file()
    assert (
        api.target / "freeze" / "lessons" / "a" / "index" / "execute-results"
    ).is_dir()


# A developer's machine (ADR 017 decision 7): the repository of the clone and
# the login of gh stand in for the variables CI sets.


def test_without_a_token_the_login_of_gh_is_used(api: Api):
    result = api.fetch(without=("GH_TOKEN",), FAKE_AUTH_EXIT="0")
    assert result.returncode == 0, output(result)
    assert api.outputs() == {"accepted": "true", "run-id": str(RUN)}


def test_without_a_token_or_a_login_there_is_no_base(api: Api):
    result = api.fetch(without=("GH_TOKEN",), FAKE_AUTH_EXIT="1")
    assert_no_base(api, result, "gh is not logged in")


def test_without_the_repository_variable_the_repository_of_the_clone_is_used(
    api: Api,
):
    result = api.fetch(without=("GITHUB_REPOSITORY",), FAKE_REPO=REPO)
    assert result.returncode == 0, output(result)
    assert api.outputs() == {"accepted": "true", "run-id": str(RUN)}
    # Another repository's clone finds no base of this one: the records of
    # the runs are read for the repository gh names.
    result = api.fetch(without=("GITHUB_REPOSITORY",), FAKE_REPO="other/repo")
    assert_no_base(api, result, "cannot be listed")


def test_without_a_repository_there_is_no_base(api: Api):
    result = api.fetch(without=("GITHUB_REPOSITORY",))
    assert_no_base(api, result, "the repository cannot be determined")


def test_the_latest_acceptable_run_wins_and_a_rejected_one_is_skipped(api: Api):
    # Listed first, so the newest; its verify failed, so the next one is taken.
    api.add_run(2000, listed=False, verify="failure")
    api.put(
        f"repos/{REPO}/actions/workflows/ci.yml/runs",
        {"workflow_runs": [{"id": 2000}, {"id": RUN}]},
    )
    result = api.fetch()
    assert result.returncode == 0, output(result)
    assert api.outputs()["run-id"] == str(RUN)
    assert "run 2000: the job verify did not conclude with success" in result.stderr


@pytest.mark.parametrize(
    ("record", "why"),
    [
        ({"event": "pull_request"}, "pull_request run, not a push run"),
        ({"event": "workflow_dispatch"}, "not a push run"),
        ({"head_branch": "feature/x"}, "not main"),
        ({"head_branch": "main-copy"}, "not main"),
        ({"head_repository": {"full_name": "fork/repo"}}, "another repository"),
        ({"repository": {"full_name": "fork/repo"}}, "another repository"),
        ({"path": ".github/workflows/other.yml"}, "not ci.yml"),
        ({"status": "in_progress"}, "has not completed"),
        ({"conclusion": "failure"}, "concluded with failure"),
        ({"conclusion": "cancelled"}, "concluded with cancelled"),
    ],
    ids=lambda value: value if isinstance(value, str) else next(iter(value)),
)
def test_a_run_that_is_not_a_verified_push_run_on_main_is_rejected(
    api: Api, record: dict, why: str
):
    # The run record decides, even when the listing offers the run and its
    # artifact carries the right name and the branch main.
    api.add_run(RUN + 1, listed=False)
    api.put(f"repos/{REPO}/actions/runs/{RUN}", {"id": RUN} | record)
    api.put(
        f"repos/{REPO}/actions/runs/{RUN}", api.read(f"repos/{REPO}/actions/runs/{RUN}")
    )
    run = api.read(f"repos/{REPO}/actions/runs/{RUN + 1}") | record | {"id": RUN}
    api.put(f"repos/{REPO}/actions/runs/{RUN}", run)
    assert_no_base(api, api.fetch(), why)


@pytest.mark.parametrize("verify", ["failure", "cancelled", "skipped"])
def test_a_main_run_whose_verify_did_not_succeed_is_rejected(api: Api, verify: str):
    api.add_run(RUN, verify=verify, listed=False)
    assert_no_base(api, api.fetch(), "the job verify did not conclude with success")


def test_a_run_without_the_job_verify_is_rejected(api: Api):
    api.put(f"repos/{REPO}/actions/runs/{RUN}/jobs", {"jobs": []})
    assert_no_base(api, api.fetch(), "the job verify did not conclude")


@pytest.mark.parametrize(
    ("record", "why"),
    [
        ({"expired": True}, "no single unexpired"),
        ({"name": "something-else"}, "no single unexpired"),
        ({"digest": None}, "no single unexpired"),
        ({"digest": "md5:abc"}, "no single unexpired"),
        ({"size_in_bytes": 0}, "no single unexpired"),
        ({"size_in_bytes": 3 * 1024**3}, "no single unexpired"),
        ({"workflow_run": {"id": 5, "head_branch": "main"}}, "no single unexpired"),
        (
            {"workflow_run": {"id": RUN, "head_branch": "feature/x"}},
            "no single unexpired",
        ),
    ],
    ids=lambda value: next(iter(value)) if isinstance(value, dict) else value,
)
def test_an_artifact_whose_record_does_not_fit_is_rejected(
    api: Api, record: dict, why: str
):
    path = f"repos/{REPO}/actions/runs/{RUN}/artifacts"
    listing = api.read(path)
    listing["artifacts"][0] |= record
    api.put(path, listing)
    assert_no_base(api, api.fetch(), why)


def test_two_artifacts_of_the_name_are_rejected(api: Api):
    api.add_artifact(RUN, 999)
    assert_no_base(api, api.fetch(), "no single unexpired")


def test_a_download_that_is_not_the_recorded_archive_is_rejected(api: Api):
    api.put_bytes(
        f"repos/{REPO}/actions/artifacts/{ARTIFACT + RUN}/zip", b"not the archive"
    )
    assert_no_base(api, api.fetch(), "digest differs")


def test_a_run_without_a_listing_gives_no_base(api: Api):
    api.api.joinpath(key(f"repos/{REPO}/actions/workflows/ci.yml/runs")).unlink()
    assert_no_base(api, api.fetch(), "cannot be listed")


def test_an_empty_listing_gives_no_base(api: Api):
    api.put(f"repos/{REPO}/actions/workflows/ci.yml/runs", {"workflow_runs": []})
    assert_no_base(api, api.fetch(), "no earlier push to main")


def only_artifact(api: Api, entries: dict[str, bytes | None], **record) -> None:
    """Replace the artifact of the run with one holding ``entries``."""
    api.put(f"repos/{REPO}/actions/runs/{RUN}/artifacts", {"artifacts": []})
    api.add_artifact(RUN, 500, entries, **record)


@pytest.mark.parametrize(
    ("entries", "why"),
    [
        ({}, "the archive is empty or not readable"),
        ({"../escape": b"x"} | good_entries(), "holds the path ../escape"),
        ({"/absolute": b"x"} | good_entries(), "holds the path /absolute"),
        ({"a/../../b": b"x"} | good_entries(), "holds the path a/../../b"),
        (
            {k: v for k, v in good_entries().items() if k != "digests.json"},
            "no digests.json",
        ),
        (
            {k: v for k, v in good_entries().items() if k != "pages.json"},
            "no pages.json",
        ),
        (
            {k: v for k, v in good_entries().items() if not k.startswith("freeze")},
            "no stored results",
        ),
        (good_entries() | {"digests.json": b"[1]"}, "not a JSON object"),
        (good_entries() | {"pages.json": b"not json"}, "not a JSON object"),
    ],
    ids=[
        "empty",
        "parent",
        "absolute",
        "nested-parent",
        "no-digests",
        "no-pages",
        "no-freeze",
        "digests-not-object",
        "pages-not-json",
    ],
)
def test_an_incomplete_or_unsafe_archive_is_rejected(
    api: Api, entries: dict[str, bytes | None], why: str
):
    only_artifact(api, entries)
    assert_no_base(api, api.fetch(), why)


def put_archive_with_link(
    api: Api, tmp_path: Path, *, link_first: bool = False, padding: int = 0
) -> None:
    """Make the one artifact of the run an archive that holds a link."""
    archive = tmp_path / "link.zip"
    link = zipfile.ZipInfo("freeze/link")
    link.create_system = 3
    link.external_attr = (stat.S_IFLNK | 0o777) << 16
    with zipfile.ZipFile(archive, "w") as zipped:
        if link_first:
            zipped.writestr(link, "/etc/passwd")
        for name, content in good_entries().items():
            zipped.writestr(name, content or b"")
        for number in range(padding):
            zipped.writestr(f"freeze/padding/{number:06d}-{'x' * 60}.txt", b"x")
        if not link_first:
            zipped.writestr(link, "/etc/passwd")
    data = archive.read_bytes()
    api.put(f"repos/{REPO}/actions/runs/{RUN}/artifacts", {"artifacts": []})
    api.add_artifact(RUN, 600)
    api.put_bytes(f"repos/{REPO}/actions/artifacts/600/zip", data)
    listing = api.read(f"repos/{REPO}/actions/runs/{RUN}/artifacts")
    listing["artifacts"][0]["digest"] = "sha256:" + hashlib.sha256(data).hexdigest()
    api.put(f"repos/{REPO}/actions/runs/{RUN}/artifacts", listing)


def test_an_archive_holding_a_link_is_rejected(api: Api, tmp_path: Path):
    put_archive_with_link(api, tmp_path)
    assert_no_base(api, api.fetch(), "holds ")


def test_a_link_before_a_listing_longer_than_a_pipe_is_found_by_the_listing(
    api: Api, tmp_path: Path
):
    """The rejection comes from the listing of the archive, not only from the
    check of what was unpacked: `unzip -Z | grep -q` must not fail with the
    SIGPIPE of unzip (pipefail) when grep stops at the first link."""
    put_archive_with_link(api, tmp_path, link_first=True, padding=4000)
    assert_no_base(api, api.fetch(), "the archive holds a link")


def test_nothing_of_the_base_is_executed(api: Api):
    marker = api.tmp / "executed"
    script = f"#!/usr/bin/env bash\ntouch {marker}\n".encode()
    only_artifact(
        api,
        good_entries() | {"run.sh": script, "freeze/hook.sh": script},
    )
    result = api.fetch()
    assert result.returncode == 0, output(result)
    assert not marker.exists()
    unpacked = api.target / "run.sh"
    assert not os.access(unpacked, os.X_OK) or unpacked.stat().st_mode & 0o111 == 0


def test_a_named_run_gets_the_same_checks(api: Api):
    result = api.fetch("--run", str(RUN))
    assert result.returncode == 0, output(result)
    assert api.outputs() == {"accepted": "true", "run-id": str(RUN)}

    api.add_run(RUN + 5, listed=False, event="pull_request")
    api.github_output.unlink()
    assert_no_base(api, api.fetch("--run", str(RUN + 5)), "not a push run")


@pytest.mark.parametrize("run", ["", "abc", "1;rm", "-1"])
def test_a_run_id_that_is_not_a_number_is_a_usage_error(api: Api, run: str):
    assert api.fetch("--run", run).returncode == 2


def test_a_failing_api_gives_no_base_and_does_not_fail_the_run(api: Api):
    for file in api.api.iterdir():
        file.unlink()
    assert_no_base(api, api.fetch(), "cannot be listed")


def test_what_an_earlier_base_left_is_replaced_even_when_none_is_accepted(api: Api):
    api.target.mkdir(parents=True)
    (api.target / "stale").write_text("old")
    api.put(f"repos/{REPO}/actions/runs/{RUN}", {"id": RUN, "event": "pull_request"})
    assert_no_base(api, api.fetch(), "not a push run")


def test_collect_base_gathers_what_a_build_left(tmp_path: Path):
    site = tmp_path / "site"
    (site / "_freeze" / "lessons" / "a").mkdir(parents=True)
    (site / "_freeze" / "lessons" / "a" / "result.json").write_text("{}")
    (site / "_digests.json").write_text("{}")
    (site / "_pages.json").write_text("{}")
    out = tmp_path / "out"
    env = {**os.environ, "PBC_SOURCE_DIR": str(site)}
    run = subprocess.run(
        [SCRIPTS / "collect-base.sh", out],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 0, output(run)
    assert sorted(
        p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file()
    ) == [
        "digests.json",
        "freeze/lessons/a/result.json",
        "pages.json",
    ]
    (site / "_pages.json").unlink()
    run = subprocess.run(
        [SCRIPTS / "collect-base.sh", out],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.returncode == 1
    assert "_pages.json is missing" in run.stderr
