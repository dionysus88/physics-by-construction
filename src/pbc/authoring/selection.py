"""The selection of a verification run against a base (ADR 014 decisions 2-5).

``./scripts/verify.sh --base <directory>`` calls this module once and writes
the result to one file, ``SELECTION_FILE``, where the checks read it. The
selection names the lessons this run executes and the lessons whose executed
results are restored from the base.

A base is a directory with ``digests.json`` (what ``pbc.authoring.digest``
writes: format, identity of the checks, input digest of every lesson) and
``freeze/`` (the executed results of every lesson, laid out as the build
writes them). Its contents are data: nothing in it is executed, and nothing in
it is read as configuration. The rule fails safe: a base that is missing,
cannot be read, is truncated, or is of another format, a lesson without a
digest, and a change to the checks give a full run, with the reason.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

from pbc.authoring.digest import FORMAT, LESSONS, Digester, check_identity
from pbc.authoring.repository import REPOSITORY_ROOT

SELECTION_FILE = ".agents/verification/selection.json"
DIGESTS = "digests.json"
STORE = "freeze"
SELECTION_FORMAT = 1


def _full(lessons: list[str], reason: str, base: dict | None) -> dict:
    return {
        "format": SELECTION_FORMAT,
        "mode": "full",
        "reason": reason,
        "base": base,
        "lessons": lessons,
        "execute": list(lessons),
        "reuse": [],
    }


def _read_base(directory: Path) -> tuple[dict | None, str]:
    """The digests of a base and the reason it cannot be used, if any."""
    path = directory / DIGESTS
    try:
        raw = path.read_bytes()
        data = json.loads(raw)
    except OSError, ValueError:
        return None, f"the base has no readable {DIGESTS}"
    if not isinstance(data, dict) or data.get("format") != FORMAT:
        return None, "the base is of another format"
    identity = data.get("identity")
    if not isinstance(identity, str) or not identity:
        return None, "the base has no identity of the checks"
    lessons = data.get("lessons")
    if not isinstance(lessons, dict) or not all(
        isinstance(v, dict) for v in lessons.values()
    ):
        return None, "the base holds no lesson digests"
    return {
        "id": hashlib.sha256(raw).hexdigest(),
        "identity": identity,
        "lessons": {k: v.get("digest") for k, v in lessons.items()},
    }, ""


def _stored(directory: Path, lesson: str) -> bool:
    """Whether the base holds executed results for ``lesson`` (a path such as
    ``site/lessons/s/01-one``; the store is laid out relative to ``site/``)."""
    store = directory / STORE / Path(lesson).relative_to("site")
    return store.is_dir() and any(p.is_file() for p in store.rglob("*"))


def select(root: Path, base: Path | None) -> dict:
    """The selection of the tree at ``root`` against the base at ``base``."""
    root = root.resolve()
    current = Digester(root).all()
    lessons = sorted(current)
    if base is None:
        return _full(lessons, "no base was given", None)
    loaded, why = _read_base(base)
    if loaded is None:
        return _full(lessons, why, None)
    named = {"id": loaded["id"], "identity": loaded["identity"]}
    missing = sorted(p for p, d in current.items() if d.value is None)
    if missing:
        return _full(
            lessons,
            f"{len(missing)} lesson(s) have no input digest (first: {missing[0]})",
            named,
        )
    if loaded["identity"] != check_identity(root):
        return _full(
            lessons,
            "the checks changed since the base (identity differs): every lesson "
            "is executed, every page checked, every lesson reproduced",
            named,
        )
    execute, reuse = [], []
    for path in lessons:
        unchanged = loaded["lessons"].get(path) == current[path].value
        if unchanged and not _stored(base, path):
            return _full(
                lessons, f"the base is truncated: no results for {path}", named
            )
        (reuse if unchanged else execute).append(path)
    return {
        "format": SELECTION_FORMAT,
        "mode": "selective",
        "reason": "",
        "base": named,
        "lessons": lessons,
        "execute": execute,
        "reuse": reuse,
    }


def write(root: Path, selection: dict) -> Path:
    target = root / SELECTION_FILE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(selection, indent=2, sort_keys=True) + "\n", "utf-8")
    return target


def read(root: Path = REPOSITORY_ROOT) -> dict | None:
    """The selection ``verify.sh`` wrote, or None when the run has no base."""
    try:
        data = json.loads((root / SELECTION_FILE).read_text("utf-8"))
    except OSError, ValueError:
        return None
    ok = isinstance(data, dict) and data.get("format") == SELECTION_FORMAT
    return data if ok else None


def summary(selection: dict) -> str:
    n, e = len(selection["lessons"]), len(selection["execute"])
    base = selection["base"]["id"][:12] if selection["base"] else "none"
    if selection["mode"] == "full":
        return (
            f"full run, base {base}: {selection['reason']} "
            f"({e} of {n} lessons executed)"
        )
    return (
        f"selective run against base {base}: {e} of {n} lessons executed, "
        f"{len(selection['reuse'])} restored"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Select what a run executes.")
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--base", type=Path, required=True)
    arguments = parser.parse_args(argv)
    selection = select(arguments.root, arguments.base)
    write(arguments.root.resolve(), selection)
    print(summary(selection))
    for path in selection["execute"][:20]:
        print(f"  execute {path.removeprefix(LESSONS + '/')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
