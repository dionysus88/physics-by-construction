"""The reports of the lesson on analysis pipelines and their expectations.

``python -m pbc.data.reports`` builds every report and says whether it matches
the committed expectation in ``reports/expected/``. With ``--update`` it writes
the expectations: do that on purpose, after a change you can explain, and read
the diff. The lesson page runs the same comparison when the site is built.
"""

import sys
from collections.abc import Callable

from pbc.data import flume_analysis
from pbc.data.pipeline import EXPECTED_DIR, Report, differences
from pbc.mechanics import analysis

REPORTS: dict[str, Callable[[], Report]] = {
    "projectile-range": analysis.build_report,
    "flume-waves": flume_analysis.build_report,
}


def main(argv: list[str]) -> int:
    update = "--update" in argv
    failed = False
    for name, build in REPORTS.items():
        report, path = build(), EXPECTED_DIR / f"{name}.txt"
        if update:
            EXPECTED_DIR.mkdir(parents=True, exist_ok=True)
            path.write_text(report.render(), encoding="utf-8")
            print(f"wrote {path}")
            continue
        expected = path.read_text(encoding="utf-8") if path.is_file() else ""
        problems = differences(report, expected)
        print(f"{name}: {'matches' if not problems else 'DIFFERS'}")
        for problem in problems:
            print(f"  {problem}")
        failed |= bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
