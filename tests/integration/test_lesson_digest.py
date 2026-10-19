"""The input digest of a lesson (ADR 014 decision 1, F61).

Each kind of input changes the digest, what is not an input does not, and a
lesson whose inputs cannot be followed has no digest. The tests run on a small
repository written to a temporary directory; one test runs on this repository.
"""

import textwrap
from pathlib import Path

import pytest
from support.paths import REPO_ROOT

from pbc.authoring.digest import Digester, check_identity, render

LESSON = "site/lessons/s/01-one"

FILES = {
    "pyproject.toml": "[project]\nname='x'\n",
    "uv.lock": "lock 1\n",
    ".python-version": "3.14\n",
    "lean/lean-toolchain": "v1\n",
    "lean/lake-manifest.json": "{}\n",
    "lean/lakefile.toml": "name='x'\n",
    "lean/PhysicsByConstruction/A.lean": "theorem a : True := trivial\n",
    "lean/PhysicsByConstruction/B.lean": "import PhysicsByConstruction.A\n",
    "lean/PhysicsByConstruction/Unused.lean": "-- unused\n",
    "src/pbc/__init__.py": "",
    "src/pbc/authoring/__init__.py": "def header(): ...\n",
    "src/pbc/mech/__init__.py": "",
    "src/pbc/mech/top.py": "from pbc.mech import middle\n",
    "src/pbc/mech/middle.py": "from . import bottom\n",
    "src/pbc/mech/bottom.py": "VALUE = 1\n",
    "src/pbc/mech/other.py": "VALUE = 2\n",
    "data/registry/ds1.yaml": "id: ds1\n",
    "data/registry/ds2.yaml": "id: ds2\n",
    "data/samples/ds1/s.csv": "1,2\n",
    "data/samples/ds2/s.csv": "3,4\n",
    "site/_quarto.yml": "project: {}\n",
    "site/_filters/f.lua": "-- f\n",
    "site/assets/a.css": "a {}\n",
    "site/index.qmd": "home\n",
    "site/glossary.yaml": "terms: []\n",
    "site/widgets/w.html": "<p>w</p>\n",
    f"{LESSON}/fixture.json": "{}\n",
    "site/lessons/s/02-two/index.qmd": (
        "---\ntitle: Two\n---\n\n```{python}\nx = 1\n```\n"
    ),
}


def _lesson(cell: str, front: str = "") -> str:
    return f"---\ntitle: One\n{front}---\n\n```{{python}}\n{textwrap.dedent(cell)}```\n"


CELL = """\
from pbc.authoring import header
from pbc.mech.top import VALUE
from pbc.data import SAMPLES_DIR

path = SAMPLES_DIR / "ds1" / "s.csv"
"""
LEAN = "lesson:\n  lean-modules:\n    - PhysicsByConstruction.B\n"


def _write(root: Path, name: str, text: str) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    for name, text in FILES.items():
        _write(tmp_path, name, text)
    _write(tmp_path, "src/pbc/data/__init__.py", 'SAMPLES_DIR = "data/samples"\n')
    _write(tmp_path, f"{LESSON}/index.qmd", _lesson(CELL, LEAN))
    return tmp_path


def digest(root: Path) -> str | None:
    return Digester(root).digest(root / LESSON).value


def reason(root: Path) -> str:
    result = Digester(root).digest(root / LESSON)
    assert result.value is None
    return result.reason or ""


def test_the_digest_is_stable(repository):
    assert digest(repository) is not None
    assert digest(repository) == digest(repository)


@pytest.mark.parametrize(
    "name",
    [
        f"{LESSON}/index.qmd",
        f"{LESSON}/fixture.json",
        "src/pbc/mech/top.py",
        "src/pbc/mech/middle.py",
        "src/pbc/mech/bottom.py",
        "src/pbc/data/__init__.py",
        "data/samples/ds1/s.csv",
        "data/registry/ds1.yaml",
        "lean/PhysicsByConstruction/B.lean",
        "lean/PhysicsByConstruction/A.lean",
        "lean/lean-toolchain",
        "lean/lake-manifest.json",
        "pyproject.toml",
        "uv.lock",
        ".python-version",
        "src/pbc/authoring/__init__.py",
        "site/_quarto.yml",
        "site/_filters/f.lua",
        "site/assets/a.css",
        "site/index.qmd",
        "site/glossary.yaml",
        "site/widgets/w.html",
    ],
)
def test_each_kind_of_input_changes_the_digest(repository, name):
    before = digest(repository)
    path = repository / name
    path.write_text(
        path.read_text(encoding="utf-8") + "\n# changed\n", encoding="utf-8"
    )
    assert digest(repository) != before


def test_the_experiment_of_a_lesson_is_an_input_of_its_digest(repository):
    # The cells import the lesson's experiment (ADR 016 decision 2), so a
    # changed entry point selects its lesson, and the check runs for it.
    _write(repository, "src/pbc/mech/experiments/__init__.py", "")
    _write(repository, "src/pbc/mech/experiments/one.py", "def run(): ...\n")
    cell = CELL + "from pbc.mech.experiments import one as experiment\n"
    _write(repository, f"{LESSON}/index.qmd", _lesson(cell, LEAN))
    before = digest(repository)

    _write(repository, "src/pbc/mech/experiments/one.py", "def run(): return 1\n")

    assert digest(repository) != before


@pytest.mark.parametrize(
    ("name", "text"),
    [
        ("site/lessons/s/02-two/index.qmd", "---\ntitle: Renamed\n---\n"),
        ("src/pbc/mech/other.py", "VALUE = 3\n"),
        ("data/samples/ds2/s.csv", "9,9\n"),
        ("data/registry/ds2.yaml", "id: ds2\nchanged: true\n"),
        ("lean/PhysicsByConstruction/Unused.lean", "-- changed\n"),
        ("site/index.html", "<p>render output</p>\n"),
        ("site/_site/index.html", "<p>render output</p>\n"),
        ("site/_freeze/x/y.json", "{}\n"),
        ("site/_digests.json", "{}\n"),
        ("site/_timings.json", "[]\n"),
        (f"{LESSON}/index.html", "<p>render output</p>\n"),
    ],
)
def test_what_is_not_an_input_leaves_the_digest(repository, name, text):
    before = digest(repository)
    _write(repository, name, text)
    assert digest(repository) == before


def test_a_module_that_computes_what_it_imports_is_an_input_of_every_lesson(repository):
    before = digest(repository)
    _write(repository, "src/pbc/mech/other.py", "import importlib\n")
    after = digest(repository)
    assert after != before
    _write(repository, "src/pbc/mech/other.py", "import importlib\nVALUE = 5\n")
    assert digest(repository) != after


def test_a_data_directory_without_a_name_is_every_dataset(repository):
    _write(
        repository,
        f"{LESSON}/index.qmd",
        _lesson(
            "from pbc.data import SAMPLES_DIR\nfiles = list(SAMPLES_DIR.glob('*'))\n"
        ),
    )
    before = digest(repository)
    _write(repository, "data/samples/ds2/s.csv", "9,9\n")
    assert digest(repository) != before


@pytest.mark.parametrize(
    ("cell", "fragment"),
    [
        ("import importlib\nimportlib.import_module('pbc.mech.top')\n", "importlib"),
        ("m = __import__('pbc')\n", "__import__"),
        ("exec('x = 1')\n", "exec"),
        ("import pbc.missing\n", "not found"),
        ("name = 'a'\nopen(name + '.txt')\n", "'name'"),
        ("open(f'{1}.txt')\n", "put together"),
        ("open('/etc/hosts')\n", "outside the repository"),
        ("url = 'https://example.org/data.csv'\n", "network"),
        ("x = (\n", "not valid Python"),
        ("%matplotlib inline\n", "magic"),
    ],
)
def test_an_input_that_cannot_be_followed_gives_no_digest(repository, cell, fragment):
    _write(repository, f"{LESSON}/index.qmd", _lesson(cell, LEAN))
    assert fragment in reason(repository)


def test_a_cell_in_another_language_gives_no_digest(repository):
    text = _lesson(CELL) + "\n```{r}\nx <- 1\n```\n"
    _write(repository, f"{LESSON}/index.qmd", text)
    assert "r" in reason(repository)


def test_an_inline_expression_is_followed(repository):
    _write(
        repository,
        f"{LESSON}/index.qmd",
        _lesson(CELL) + "\nA value: `{python} VALUE`.\n",
    )
    assert digest(repository) is not None
    _write(
        repository,
        f"{LESSON}/index.qmd",
        _lesson(CELL) + "\nA value: `{python} __import__('os')`.\n",
    )
    assert "__import__" in reason(repository)


def test_a_lean_module_that_is_missing_gives_no_digest(repository):
    _write(
        repository,
        f"{LESSON}/index.qmd",
        _lesson(CELL, "lesson:\n  lean-modules: [PhysicsByConstruction.Gone]\n"),
    )
    assert "Gone" in reason(repository)


def test_every_lesson_of_this_repository_has_a_digest():
    digests = Digester(REPO_ROOT).all()
    assert digests
    missing = {path: d.reason for path, d in digests.items() if d.value is None}
    assert not missing
    assert len({d.value for d in digests.values()}) == len(digests)
    assert render(REPO_ROOT).startswith("{")


PIPELINE = (
    "from pathlib import Path\n\n"
    'EXPECTED_DIR = Path(__file__).resolve().parents[3] / "reports" / "expected"\n'
    'NAME = "r.txt"\n'
)


def _expectations(root: Path, use: str, cell: str = "from pbc.mech import report\n"):
    """A module of ``pbc`` that exports a path below the repository, and a
    lesson that reaches it through ``src/pbc/mech/report.py``."""
    _write(root, "src/pbc/data/pipeline.py", PIPELINE)
    _write(root, "reports/expected/r.txt", "range 1\n")
    _write(root, "reports/expected/other.txt", "other 1\n")
    _write(root, "src/pbc/mech/report.py", use)
    _write(root, f"{LESSON}/index.qmd", _lesson(CELL + cell, LEAN))


REPORT = "from pbc.data.pipeline import EXPECTED_DIR\n\n"


@pytest.mark.parametrize(
    "use",
    [
        REPORT + "def check():\n    return (EXPECTED_DIR / 'r.txt').read_text()\n",
        REPORT + "def check():\n    return EXPECTED_DIR.joinpath('r.txt')\n",
        "from pbc.data.pipeline import EXPECTED_DIR as E, NAME\n\n"
        "def check():\n    return E / NAME\n",
        "from pbc.data import pipeline\n\n"
        "def check():\n    return pipeline.EXPECTED_DIR / pipeline.NAME\n",
        "import pbc.data.pipeline\n\n"
        "def check():\n    return pbc.data.pipeline.EXPECTED_DIR / 'r.txt'\n",
        "from ..data.pipeline import EXPECTED_DIR\n\n"
        "PATH = EXPECTED_DIR / 'r.txt'\nTEXT = PATH.read_text()\n",
    ],
)
def test_a_file_that_an_exported_path_names_is_an_input(repository, use):
    # F61 follow-up M2: a lesson that compares with a committed expectation
    # in reports/expected depends on that file, not only on the module.
    _expectations(repository, use)
    before = digest(repository)
    assert before is not None
    _write(repository, "reports/expected/other.txt", "other 2\n")
    assert digest(repository) == before
    _write(repository, "reports/expected/r.txt", "range 2\n")
    after = digest(repository)
    assert after != before
    (repository / "reports/expected/r.txt").unlink()
    assert digest(repository) not in {before, after}


def test_a_path_used_with_a_computed_part_is_its_whole_directory(repository):
    _expectations(repository, REPORT + "def check(n):\n    return EXPECTED_DIR / n\n")
    before = digest(repository)
    _write(repository, "reports/expected/other.txt", "other 2\n")
    after = digest(repository)
    assert after != before
    _write(repository, "reports/expected/new.txt", "new\n")
    assert digest(repository) != after


def test_an_exported_path_in_a_cell_is_followed(repository):
    _expectations(
        repository,
        "VALUE = 1\n",
        "from pbc.data.pipeline import EXPECTED_DIR\n"
        "text = (EXPECTED_DIR / 'r.txt').read_text()\n",
    )
    before = digest(repository)
    _write(repository, "reports/expected/other.txt", "other 2\n")
    assert digest(repository) == before
    _write(repository, "reports/expected/r.txt", "range 2\n")
    assert digest(repository) != before


def test_an_exported_path_that_is_not_used_is_no_input(repository):
    # Defining a constant reads nothing: importing the module that defines
    # it does not make its files inputs of the lesson.
    _expectations(repository, "from pbc.data import pipeline\n\nVALUE = 1\n")
    before = digest(repository)
    _write(repository, "reports/expected/r.txt", "range 2\n")
    assert digest(repository) == before


@pytest.mark.parametrize(
    ("use", "fragment"),
    [
        ("import os\n\nHERE = os.path.dirname(__file__)\n", "__file__"),
        (
            "from pathlib import Path\n\nROOT = Path(__file__).parents[3]\n\n"
            "def files():\n    return ROOT\n",
            "whole repository",
        ),
        (
            "from pathlib import Path\n\nUP = Path(__file__).parents[9] / 'x'\n",
            "leaves the repository",
        ),
        (
            REPORT + "def check():\n    return EXPECTED_DIR / '/etc/passwd'\n",
            "leaves the repository",
        ),
    ],
)
def test_a_path_the_digester_cannot_decide_gives_no_digest(repository, use, fragment):
    # The lesson then counts as depending on everything: it is executed.
    _expectations(repository, use)
    assert fragment in reason(repository)
    # A lesson that does not reach the module keeps its digest.
    other = Digester(repository).digest(repository / "site/lessons/s/02-two")
    assert other.value is not None


COMPUTED = (
    "from pathlib import Path\n\n"
    "def make_expected_dir():\n"
    "    return Path(__file__).resolve().parents[3] / 'reports' / 'expected'\n\n"
)


@pytest.mark.parametrize(
    ("pipeline", "use"),
    [
        (COMPUTED + "EXPECTED_DIR = make_expected_dir()\n", REPORT),
        (
            COMPUTED + "EXPECTED = make_expected_dir()\n",
            "from pbc.data.pipeline import EXPECTED as EXPECTED_DIR\n\n",
        ),
        ("from somewhere import locate\n\nEXPECTED_DIR = locate()\n", REPORT),
        (
            "import os\n\nEXPECTED_DIR = os.environ['EXPECTED']\n",
            "from pbc.data import pipeline\n\n",
        ),
        (
            "from pathlib import Path\n\ntry:\n"
            "    EXPECTED_DIR = Path(__file__).parents[3] / 'reports'\n"
            "except OSError:\n    EXPECTED_DIR = None\n",
            REPORT,
        ),
        (
            COMPUTED + "BASE = make_expected_dir()\nEXPECTED_DIR = BASE / 'x'\n",
            REPORT,
        ),
    ],
)
def test_an_exported_path_that_cannot_be_decided_gives_no_digest(
    repository, pipeline, use
):
    # Triage M1: a path constant the digester cannot decide is no input it
    # can name; the lesson that uses it counts as depending on everything.
    _expectations(repository, use)
    _write(repository, "src/pbc/data/pipeline.py", pipeline)
    if "EXPECTED_DIR" not in use:
        use += "def check():\n    return pipeline.EXPECTED_DIR / 'r.txt'\n"
    else:
        use += "def check():\n    return (EXPECTED_DIR / 'r.txt').read_text()\n"
    _write(repository, "src/pbc/mech/report.py", use)
    assert "cannot be followed" in reason(repository)
    other = Digester(repository).digest(repository / "site/lessons/s/02-two")
    assert other.value is not None


def test_a_computed_exported_path_used_in_a_cell_gives_no_digest(repository):
    _expectations(
        repository,
        "VALUE = 1\n",
        "from pbc.data.pipeline import EXPECTED_DIR\n"
        "text = (EXPECTED_DIR / 'r.txt').read_text()\n",
    )
    _write(
        repository,
        "src/pbc/data/pipeline.py",
        COMPUTED + "EXPECTED_DIR = make_expected_dir()\n",
    )
    assert "EXPECTED_DIR may be a path" in reason(repository)


@pytest.mark.parametrize(
    "constant",
    [
        "FILES = {'a': 'a.txt'}\n",
        "MAX_FILE = 2 * 1024 * 1024\n",
        "from typing import Callable\n\nPath = Callable[[float], float]\n",
        "SCALE = compute()\n\ndef compute():\n    return 2.0\n",
    ],
)
def test_a_constant_that_is_no_path_keeps_the_digest(repository, constant):
    _expectations(repository, REPORT + "def check():\n    return EXPECTED_DIR\n")
    _write(repository, "src/pbc/data/extra.py", constant)
    name = constant.split(" =")[0].split("\n")[-1]
    _write(
        repository,
        "src/pbc/mech/report.py",
        f"from pbc.data.extra import {name}\n\ndef check():\n    return {name}\n",
    )
    assert digest(repository) is not None


def test_the_pipeline_lesson_of_this_repository_follows_its_expectations():
    digester = Digester(REPO_ROOT)
    lesson = REPO_ROOT / "site/lessons/mechanics/10-automated-analysis-pipelines"
    files = digester.lesson_files(lesson)
    assert "reports/expected/projectile-range.txt" in files
    assert "reports/expected/flume-waves.txt" in files
    unrelated = digester.lesson_files(
        REPO_ROOT / "site/lessons/mechanics/01-kinematics-as-a-program"
    )
    assert not any(name.startswith("reports/") for name in unrelated)


IDENTITY_FILES = [
    "scripts/verify.sh",
    "scripts/verify.conf",
    "scripts/build-site.sh",
    "scripts/check-determinism.sh",
    "pyproject.toml",
    "uv.lock",
    ".github/actions/prepare/action.yml",
    "tests/e2e/test_page.py",
    "tests/e2e/shards.json",
    "tests/support/checks.py",
]


@pytest.fixture
def checks(tmp_path: Path) -> Path:
    for name in IDENTITY_FILES:
        _write(tmp_path, name, "1\n")
    return tmp_path


@pytest.mark.parametrize("name", IDENTITY_FILES)
def test_each_input_of_the_identity_changes_it(checks, name):
    before = check_identity(checks)
    assert check_identity(checks) == before
    _write(checks, name, "2\n")
    assert check_identity(checks) != before


def test_a_new_check_file_changes_the_identity(checks):
    before = check_identity(checks)
    _write(checks, "tests/support/new.py", "1\n")
    assert check_identity(checks) != before


def test_an_integration_test_does_not_change_the_identity(checks):
    # F119: no check a base reduces reads tests/integration, and the checks
    # that run it are never reduced by a base (docs/verification-audit.md).
    before = check_identity(checks)
    _write(checks, "tests/integration/test_x.py", "1\n")
    assert check_identity(checks) == before
    _write(checks, "tests/integration/test_x.py", "2\n")
    assert check_identity(checks) == before


def test_a_lesson_does_not_change_the_identity(checks):
    before = check_identity(checks)
    _write(checks, "site/lessons/s/01-one/index.qmd", "x\n")
    _write(checks, "src/pbc/mech/a.py", "x\n")
    assert check_identity(checks) == before


READERS = [
    "from pathlib import Path\n(Path('..') / 'outside.csv').read_text()\n",
    "from pathlib import Path\nPath('a').joinpath('..', 'o.csv').read_text()\n",
    "from pathlib import Path\nPath('a/b').with_name('..').read_text()\n",
    "from pathlib import Path\nPath('a/../../o.csv').read_text()\n",
    "from pathlib import Path\n(Path('a') / '/etc/passwd').read_text()\n",
    "from pathlib import Path\n(Path('.') / ('.' + '.') / 'o.csv').read_text()\n",
    "from pathlib import Path\nPath('a').parent.parent.joinpath('o').read_text()\n",
    "from pathlib import Path\nPath('a').parents[3].joinpath('o').read_text()\n",
    "from pathlib import Path\nPath('~/o.csv').read_text()\n",
    "from pathlib import Path\nPath('fixture.csv').resolve().read_text()\n",
    "from pathlib import Path\nPath('a').absolute().read_text()\n",
    "from pathlib import Path\nPath('a').readlink().read_text()\n",
    "from pathlib import Path\nPath('a').expanduser().read_text()\n",
    "import pandas as pd\nfrom pathlib import Path\npd.read_csv(Path('..') / 'o')\n",
    "import pandas\npandas.read_csv('/outside/file.csv')\n",
    "import pandas as pd\npd.read_csv('/outside/file.csv')\n",
    "from pandas import read_csv\nread_csv('/outside/file.csv')\n",
    "import numpy as np\nnp.load('../outside.npy')\n",
    "import numpy as np\nnp.loadtxt(path)\n",
    "import pandas as pd\npd.read_csv(filepath_or_buffer=other)\n",
    "from pathlib import Path\nPath('/outside/f.txt').open()\n",
    "from pathlib import Path\nPath('/outside/f.txt').read_text()\n",
    "from pathlib import Path\np = Path.home()\np.open()\n",
    "from pathlib import Path\nfor p in Path('/outside').glob('*'):\n    pass\n",
    "import pandas as pd\nreader = pd.read_csv\n",
    "import os\nos.listdir(folder)\n",
    "path.read_bytes()\n",
]


@pytest.mark.parametrize("cell", READERS)
def test_a_read_outside_the_known_locations_gives_no_digest(repository, cell):
    _write(repository, f"{LESSON}/index.qmd", _lesson(cell, LEAN))
    assert reason(repository)


@pytest.mark.parametrize(
    "cell",
    [
        "from pbc.data import SAMPLES_DIR\nimport pandas as pd\n"
        "pd.read_csv(SAMPLES_DIR / 'ds1' / 's.csv')\n",
        "from pbc.data import SAMPLES_DIR\n"
        "p = SAMPLES_DIR / 'ds1' / 's.csv'\np.open()\np.read_text()\n",
        "from pbc.data import SAMPLES_DIR\n"
        "for p in sorted(SAMPLES_DIR.glob('ds1/*')):\n    p.read_text()\n",
        "from pathlib import Path\nPath('fixture.json').open()\n",
    ],
)
def test_a_read_in_a_known_location_has_a_digest(repository, cell):
    _write(repository, f"{LESSON}/index.qmd", _lesson(cell, LEAN))
    assert digest(repository) is not None


@pytest.mark.parametrize(
    "cell",
    [
        "import importlib.util as iu\niu.find_spec('x')\n",
        "import importlib.util as iu\n",
        "import importlib.util\n",
        "import importlib.machinery as m\n",
        "from importlib import util\n",
        "from importlib.util import find_spec as f\n",
        "import builtins\n",
        "import runpy as r\nr.run_path('x.py')\n",
        "from importlib import import_module as im\nim('x')\n",
    ],
)
def test_a_dynamic_import_by_any_alias_gives_no_digest(repository, cell):
    _write(repository, f"{LESSON}/index.qmd", _lesson(cell, LEAN))
    assert "loads code by name" in reason(repository)


DATA_CELL = "from pbc.data import SAMPLES_DIR\nfrom pbc.data.reader import load_set\n"


def _reader_repository(root: Path, cell: str, names: bool = False) -> None:
    where = "SAMPLES_DIR / 'ds1' / name" if names else "SAMPLES_DIR / name"
    _write(
        root,
        "src/pbc/data/reader.py",
        "from pbc.data import SAMPLES_DIR\n\n"
        f"def load_set(name):\n    return {where}\n",
    )
    _write(root, f"{LESSON}/index.qmd", _lesson(DATA_CELL + cell, LEAN))


@pytest.mark.parametrize("name", ["data/samples/ds2/s.csv", "data/registry/ds2.yaml"])
def test_a_dataset_that_a_reader_gets_indirectly_changes_the_digest(repository, name):
    _reader_repository(repository, "which = 'd' + 's2'\nload_set(which)\n")
    before = digest(repository)
    _write(repository, name, "9,9\n")
    assert digest(repository) != before


def test_a_dataset_named_to_a_reader_is_the_only_one_that_counts(repository):
    _reader_repository(repository, "load_set('s.csv')\n", names=True)
    before = digest(repository)
    _write(repository, "data/samples/ds2/s.csv", "9,9\n")
    assert digest(repository) == before
    _write(repository, "data/samples/ds1/s.csv", "9,9\n")
    assert digest(repository) != before


def test_a_module_that_reads_a_directory_without_a_name_reads_every_dataset(
    repository,
):
    _write(
        repository,
        "src/pbc/mech/scan.py",
        "from pbc.data import SAMPLES_DIR\nFILES = list(SAMPLES_DIR.glob('*'))\n",
    )
    _write(repository, f"{LESSON}/index.qmd", _lesson("import pbc.mech.scan\n", LEAN))
    before = digest(repository)
    _write(repository, "data/samples/ds2/s.csv", "9,9\n")
    assert digest(repository) != before


def test_the_tools_of_the_data_package_are_those_of_the_data_use_analysis():
    from support.data_use import TOOLS

    from pbc.authoring.digest import _DATA_TOOLS

    assert _DATA_TOOLS == TOOLS
