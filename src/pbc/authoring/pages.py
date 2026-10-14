"""Which built pages differ from the base (ADR 014 decision 3).

A build records the checksum of every file of the site with the build commit
normalised: the commit is the one value every page that shows provenance
carries and that changes with every commit, so two builds of the same sources
at two commits would otherwise differ on every lesson page. A run with a base
compares its own record with the record of the base. The checks of one page
(accessibility, reading without scripts, widths, payload) run for the pages
whose normalised bytes differ, which includes every page of a lesson this run
executed.

The record of a base is data; nothing in it is executed or read as
configuration, and a record that cannot be read selects every page.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

from pbc.authoring import selection as selecting
from pbc.authoring.repository import REPOSITORY_ROOT, build_commit

PAGES = "pages.json"
BUILT_PAGES = "_pages.json"
FORMAT = 1
PLACEHOLDER = b"PBC-BUILD-COMMIT"


def _checksum(data: bytes, commit: str | None) -> str:
    if commit:
        data = data.replace(commit.encode(), PLACEHOLDER)
    return hashlib.sha256(data).hexdigest()


def record(site_dir: Path, commit: str | None) -> dict:
    """The record of the built site in ``site_dir`` built from ``commit``."""
    files = {}
    for path in sorted(site_dir.rglob("*")):
        if path.is_file():
            files[path.relative_to(site_dir).as_posix()] = _checksum(
                path.read_bytes(), commit
            )
    return {"format": FORMAT, "files": files}


def read(path: Path) -> dict | None:
    """The record at ``path``, or None when it cannot be used."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return None
    if not isinstance(data, dict) or data.get("format") != FORMAT:
        return None
    files = data.get("files")
    if not isinstance(files, dict):
        return None
    if not all(isinstance(k, str) and isinstance(v, str) for k, v in files.items()):
        return None
    return data


def pages(site_dir: Path) -> list[str]:
    """Every HTML page of the built site, relative to it."""
    return sorted(p.relative_to(site_dir).as_posix() for p in site_dir.rglob("*.html"))


def differing(site_dir: Path, base: dict, commit: str | None) -> list[str]:
    """The pages of ``site_dir`` that are not byte-identical to the page of the
    base, with the build commit normalised in both, and the pages the base does
    not have."""
    current = record(site_dir, commit)["files"]
    known = base["files"]
    return [page for page in pages(site_dir) if known.get(page) != current[page]]


def _lesson_page(lesson: str) -> str:
    """The built page of a lesson directory (``site/lessons/s/01-one``)."""
    return f"{Path(lesson).relative_to('site').as_posix()}/index.html"


def selected(site_dir: Path, root: Path = REPOSITORY_ROOT) -> list[str] | None:
    """The pages the per-page checks run for, or None for every page.

    Every page whose bytes differ from the base's, and every page of a lesson
    this run executed. A run without a base, a full run, or a base without a
    usable record selects every page.
    """
    selection = selecting.read(root)
    if selection is None or selection.get("mode") != "selective":
        return None
    directory = selection.get("base_directory")
    if not isinstance(directory, str):
        return None
    base = read(Path(directory) / PAGES)
    if base is None:
        return None
    chosen = set(differing(site_dir, base, build_commit().sha))
    chosen |= {_lesson_page(lesson) for lesson in selection["execute"]}
    return sorted(chosen & set(pages(site_dir)))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="The record of a built site.")
    parser.add_argument("--site-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args(argv)
    data = record(arguments.site_dir, build_commit().sha)
    arguments.out.write_text(
        json.dumps(data, indent=0, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Recorded {len(data['files'])} files of the built site.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
