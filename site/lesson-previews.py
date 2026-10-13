"""Write the preview of every lesson into the built site (F63).

Runs after the site is rendered (``post-render``), before the learning path
export that names the previews. The figure of the cell a lesson names in
``lesson.preview`` is scaled to the fixed preview size; a lesson that names
none gets the conceptual fallback. Fails a full render when a named cell drew
no figure. Idempotent; the same build gives the same bytes.
"""

import os
from pathlib import Path

from pbc.authoring.path import LearningPath
from pbc.authoring.previews import write_previews


def main() -> None:
    output = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site"))
    project = Path(os.environ.get("QUARTO_PROJECT_DIR", "."))
    # Quarto sets this only when the whole project is rendered; a render of one
    # page has built the figures of that page alone.
    complete = bool(os.environ.get("QUARTO_PROJECT_RENDER_ALL"))
    write_previews(LearningPath.read(project), project, output, complete)


if __name__ == "__main__":
    main()
