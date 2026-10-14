"""Regenerate the context of every built page (ADR 014 decision 9).

The header of a lesson and the commit that "Reproduce this" and the code and
Lean excerpts name are not part of what a lesson's cells compute: the cells
leave markers (``pbc.authoring.context``), and this script, which runs after
the site is rendered (``post-render`` in ``_quarto.yml``), replaces each marker
by the region it stands for, from the current front matter, the current
curriculum, and the commit of the run. A page restored from the store of an
earlier run therefore shows the navigation and the commit of this run.

It fails the build when a marker is not valid, when a lesson page lacks a
region it must have, or when a marker would remain. It runs before every other
post-render script, which read the finished pages.
"""

import os
import sys
from pathlib import Path

from pbc.authoring.context import InvalidContext, regenerate


def main() -> None:
    output = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site"))
    try:
        pages = regenerate(output, Path.cwd())
    except InvalidContext as error:
        print(
            f"ERROR: the context of the pages cannot be regenerated: {error}",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"Context regenerated on {len(pages)} page(s).")


if __name__ == "__main__":
    main()
