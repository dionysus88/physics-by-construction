"""The input digest of a lesson (ADR 014 decision 1).

A lesson is unchanged when its digest equals the digest of the verified base.
The digest is a hash over the content of everything the scientific cells of a
lesson are computed from:

- the lesson directory (source, replay fixture, everything in it);
- every module of ``src/pbc`` that its executed cells import, followed
  through the imports of those modules;
- the dataset samples and cards it names (a string in a cell or in an
  imported module that holds the identifier of a dataset), or all of them
  when a cell reads a data directory without naming one;
- the Lean modules it displays (``lean-modules``), followed through their
  imports;
- what every lesson depends on: ``pyproject.toml``, ``uv.lock``,
  ``.python-version``, the Lean toolchain and manifest, ``src/pbc/authoring``,
  every shared file of ``site/``, and every module of ``src/pbc`` that
  imports in a way this analysis cannot follow (its importers are unknown).

The front matter of other lessons and the build commit are left out on
purpose: they feed the presentation that ADR 014 decision 9 regenerates.

When the inputs cannot be followed with certainty (a dynamic import, a path
that is put together from parts, a cell in another language, a read outside
the known locations, a module or file that is missing), the lesson has no
digest and the run is a full run. ``python -m pbc.authoring.digest`` writes
the digests of every lesson.
"""

import argparse
import ast
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from pbc.authoring.repository import REPOSITORY_ROOT

FORMAT = 1
LESSONS = "site/lessons"
PAGE = "index.qmd"

_PACKAGE_ROOT = "src"
_PINS = ("pyproject.toml", "uv.lock", ".python-version")
_LEAN_ROOT = "lean"
_LEAN_SHARED = ("lean-toolchain", "lake-manifest.json", "lakefile.toml")
_DATA_DIRECTORY_NAMES = {"SAMPLES_DIR", "DOWNLOADS_DIR", "REGISTRY_DIR"}
_DATA_PATH = re.compile(r"\bdata/(?:samples|downloads|registry)\b")

# Names that load code or run text as code, as a module of an import path, a
# name, or an attribute.
_DYNAMIC = {
    "__import__",
    "__builtins__",
    "builtins",
    "import_module",
    "importlib",
    "imp",
    "zipimport",
    "module_from_spec",
    "exec_module",
    "load_module",
    "SourceFileLoader",
    "exec",
    "eval",
    "compile",
    "runpy",
    "run_module",
    "run_path",
    "pkgutil",
    "find_spec",
    "spec_from_file_location",
}
# Calls that read a file, or list a directory, by a path: the path is the
# first argument of a function of a module, and the receiver of a method.
_READERS = {
    "open",
    "read_text",
    "read_bytes",
    "load",
    "loadtxt",
    "genfromtxt",
    "fromfile",
    "memmap",
    "loadmat",
    "imread",
    "read_csv",
    "read_table",
    "read_json",
    "read_excel",
    "read_parquet",
    "read_feather",
    "read_hdf",
    "read_pickle",
    "read_fwf",
    "read_xml",
    "read_html",
    "read_sql",
    "read_stata",
    "read_sas",
    "read_orc",
    "read_clipboard",
    "open_dataset",
    "glob",
    "rglob",
    "iterdir",
    "listdir",
    "scandir",
    "walk",
    "urlopen",
    "urlretrieve",
}
# What ``Path`` calls build a path from.
_PATH_CLASSES = {"Path", "PurePath", "PosixPath"}
# The modules of ``pbc.data`` that compute, draw, or describe and read no data;
# this is ``TOOLS`` of ``tests/support/data_use.py`` (a test keeps them equal).
_DATA_PACKAGE = "pbc.data"
_DATA_TOOLS = frozenset(
    f"{_DATA_PACKAGE}.{name}"
    for name in (
        "calibration",
        "card",
        "check",
        "fit",
        "inverse",
        "pipeline",
        "plotting",
        "series",
        "status",
        "uncertainty",
    )
)

_FENCE = re.compile(r"^(\s*)(`{3,})\{([A-Za-z0-9_-]+)[^}]*\}\s*$")
_INLINE = re.compile(r"(?<!`)`\{python\}[ \t]+([^`\n]+)`(?!`)")
_URL = re.compile(r"^[a-z][a-z0-9+.-]*://", re.I)
_LEAN_IMPORT = re.compile(r"^import\s+(\S+)", re.M)

# Site files that a render writes next to the sources, and the store.
_SITE_SKIP_DIRS = {"lessons", "_site", "_freeze", ".quarto", "site_libs", "__pycache__"}
# What a build writes at the top of the site besides the store (store.py).
_SITE_SKIP_FILES = {"_digests.json", "_timings.json", "_pages.json"}


class Unfollowable(Exception):
    """The inputs of a lesson cannot be followed with certainty."""


@dataclass(frozen=True)
class LessonDigest:
    """The digest of a lesson, or the reason why it has none."""

    value: str | None
    reason: str | None = None


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_output(path: Path) -> bool:
    name = path.name
    return (
        name.endswith((".quarto_ipynb", ".pyc"))
        or "__pycache__" in path.parts
        or any(part.endswith("_files") or part == ".quarto" for part in path.parts)
    )


def _files_under(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        p
        for p in directory.rglob("*")
        if p.is_file() and not _is_output(p.relative_to(directory))
    )


class Digester:
    """Computes the digests of the lessons of one repository."""

    def __init__(self, root: Path = REPOSITORY_ROOT):
        self.root = root.resolve()
        self._trees: dict[Path, ast.AST | None] = {}
        self._shared: dict[str, str] | None = None

    # -- files ---------------------------------------------------------------

    def _label(self, path: Path) -> str:
        return path.relative_to(self.root).as_posix()

    def _entry(self, path: Path) -> tuple[str, str]:
        try:
            return self._label(path), _sha(path.read_bytes())
        except OSError as error:
            raise Unfollowable(f"cannot read {self._label(path)}: {error}") from error

    def _tree(self, path: Path) -> ast.AST | None:
        if path not in self._trees:
            try:
                self._trees[path] = ast.parse(path.read_text(encoding="utf-8"))
            except OSError, SyntaxError, UnicodeDecodeError:
                self._trees[path] = None
        return self._trees[path]

    # -- what every lesson depends on -----------------------------------------

    def _shared_files(self) -> list[Path]:
        root = self.root
        files = [root / name for name in _PINS]
        files += [root / _LEAN_ROOT / name for name in _LEAN_SHARED]
        files += _files_under(root / _PACKAGE_ROOT / "pbc" / "authoring")
        files.append(root / _PACKAGE_ROOT / "pbc" / "__init__.py")
        site = root / "site"
        for path in sorted(site.rglob("*")) if site.is_dir() else []:
            relative = path.relative_to(site)
            if not path.is_file() or _is_output(relative):
                continue
            if (
                relative.parts[0] in _SITE_SKIP_DIRS
                or relative.name in _SITE_SKIP_FILES
            ):
                continue
            # HTML next to the sources is render output, except widgets and
            # the directories whose names start with an underscore.
            if (
                path.suffix == ".html"
                and relative.parts[0] != "widgets"
                and not relative.parts[0].startswith("_")
            ):
                continue
            files.append(path)
        files += self._opaque_modules()
        return files

    def _opaque_modules(self) -> list[Path]:
        """Modules of ``src/pbc`` whose importers cannot be known.

        A module that loads code by a name it computes can bring in any other
        module, so nobody can say which lessons depend on it: it is an input
        of every lesson.
        """
        found = []
        for path in _files_under(self.root / _PACKAGE_ROOT / "pbc"):
            if path.suffix != ".py":
                continue
            tree = self._tree(path)
            if tree is None or _dynamic_names(tree):
                found.append(path)
        return found

    def shared(self) -> dict[str, str]:
        if self._shared is None:
            self._shared = dict(self._entry(p) for p in self._shared_files())
        return self._shared

    # -- python modules ---------------------------------------------------------

    def _module_path(self, dotted: str) -> list[Path] | None:
        """The files that importing ``dotted`` runs, or None if it is missing."""
        parts = dotted.split(".")
        base = self.root / _PACKAGE_ROOT
        files = []
        for end in range(1, len(parts)):
            init = base.joinpath(*parts[:end], "__init__.py")
            if init.is_file():
                files.append(init)
        module = base.joinpath(*parts)
        if module.with_suffix(".py").is_file():
            files.append(module.with_suffix(".py"))
        elif (module / "__init__.py").is_file():
            files.append(module / "__init__.py")
        else:
            return None
        return files

    def _imports(
        self, tree: ast.AST, package: list[str]
    ) -> list[tuple[str, list[str]]]:
        """The ``pbc`` modules ``tree`` imports, each with the names taken from it."""
        found: list[tuple[str, list[str]]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found += [(a.name, []) for a in node.names if _in_package(a.name)]
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    if node.level > len(package):
                        raise Unfollowable("a relative import leaves the package")
                    prefix = package[: len(package) - node.level + 1]
                    module = ".".join(
                        [*prefix, *([node.module] if node.module else [])]
                    )
                else:
                    module = node.module or ""
                if _in_package(module):
                    found.append((module, [a.name for a in node.names]))
        return found

    def _closure(
        self, tree: ast.AST, package: list[str]
    ) -> tuple[dict[Path, None], list[ast.AST]]:
        """Every file reached from ``tree`` through ``pbc`` imports, with trees."""
        reached: dict[Path, None] = {}
        trees = [tree]
        waiting = [(tree, package)]
        while waiting:
            current, current_package = waiting.pop()
            for module, names in self._imports(current, current_package):
                targets = [module, *(f"{module}.{n}" for n in names if n != "*")]
                for dotted in targets:
                    files = self._module_path(dotted)
                    if files is None:
                        if dotted == module:
                            raise Unfollowable(f"{dotted} is imported and not found")
                        continue  # a name taken from the module, not a module
                    for file in files:
                        if file in reached:
                            continue
                        reached[file] = None
                        parsed = self._tree(file)
                        if parsed is None:
                            raise Unfollowable(f"{self._label(file)} cannot be parsed")
                        trees.append(parsed)
                        file_package = file.relative_to(
                            self.root / _PACKAGE_ROOT
                        ).parent.parts
                        waiting.append((parsed, list(file_package)))
        return reached, trees

    # -- datasets -----------------------------------------------------------------

    def _dataset_ids(self) -> list[str]:
        ids = {p.stem for p in (self.root / "data" / "registry").glob("*.yaml")}
        samples = self.root / "data" / "samples"
        if samples.is_dir():
            ids |= {p.name for p in samples.iterdir() if p.is_dir()}
        return sorted(ids)

    def _dataset_files(self, identifier: str) -> list[Path]:
        data = self.root / "data"
        files = _files_under(data / "samples" / identifier)
        files += _files_under(data / "downloads" / identifier)
        card = data / "registry" / f"{identifier}.yaml"
        if card.is_file():
            files.append(card)
        return files

    # -- lean ---------------------------------------------------------------------

    def _lean_files(self, modules: list[str]) -> list[Path]:
        reached: dict[Path, None] = {}
        waiting = list(modules)
        while waiting:
            name = waiting.pop()
            if not re.fullmatch(r"[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)*", name):
                raise Unfollowable(f"{name!r} is not a Lean module name")
            path = self.root / _LEAN_ROOT / (name.replace(".", "/") + ".lean")
            if not path.is_file():
                raise Unfollowable(f"the Lean module {name} is not in the repository")
            if path in reached:
                continue
            reached[path] = None
            text = path.read_text(encoding="utf-8")
            waiting += [
                m
                for m in _LEAN_IMPORT.findall(text)
                if m.startswith("PhysicsByConstruction")
            ]
        return list(reached)

    # -- the lesson -----------------------------------------------------------------

    def lesson_files(self, lesson: Path) -> dict[str, str]:
        """The files a lesson's digest covers, with the hash of each."""
        lesson = lesson if lesson.is_absolute() else self.root / lesson
        page = lesson / PAGE
        text = page.read_text(encoding="utf-8")
        cells, inline = _cells(text)
        trees = []
        for code in [*cells, *inline]:
            try:
                tree = ast.parse(code, mode="eval" if code in inline else "exec")
            except SyntaxError as error:
                raise Unfollowable(
                    f"a cell is not valid Python: {error.msg}"
                ) from error
            trees.append(tree)
        # A render writes the page next to its source; it is output.
        files: dict[Path, None] = {
            p: None for p in _files_under(lesson) if p.suffix != ".html"
        }
        lesson_strings: list[str] = []
        sources: set[str] = set()
        directory = False
        everything = False
        named: set[str] = set()
        ids = self._dataset_ids()
        exported = frozenset().union(*(_pbc_names(t) for t in trees))
        for tree in trees:
            names = _dynamic_names(tree)
            if names:
                raise Unfollowable(
                    f"a cell loads code by name ({', '.join(sorted(names))})"
                )
            _check_reads(tree, exported)
            lesson_strings += _strings(tree)
            directory |= _names_directory(tree)
            sources |= self._source_names(tree)
        everything |= any(_calls_with_unknown(t, sources) for t in trees)
        for tree in trees:
            reached, reached_trees = self._closure(tree, [])
            files.update(reached)
            for module_tree, module_file in zip(
                reached_trees[1:], reached, strict=True
            ):
                if "authoring" in module_file.parts:
                    continue
                strings = _strings(module_tree)
                found = _named(ids, strings)
                named |= found
                # A module that reads a data directory and names no dataset
                # reads whichever it finds there.
                everything |= _reads_directory(module_tree) and not found
        for string in lesson_strings:
            if _URL.match(string):
                raise Unfollowable(f"a cell names a network address ({string[:40]})")
            if string.startswith(("/", "~", "..")) and "/" in string:
                raise Unfollowable(
                    f"a cell reads outside the repository ({string[:40]})"
                )
        in_lesson = _named(ids, lesson_strings)
        named |= in_lesson
        directory |= any(_DATA_PATH.search(s) for s in lesson_strings)
        everything |= directory and not in_lesson
        for identifier in ids if everything else sorted(named):
            files.update(dict.fromkeys(self._dataset_files(identifier)))
        files.update(dict.fromkeys(self._lean_for(text)))
        entries = dict(self._entry(p) for p in files)
        entries.update({f"shared:{k}": v for k, v in self.shared().items()})
        return entries

    def _source_names(self, tree: ast.AST) -> set[str]:
        """The names a cell binds to a ``pbc`` module that reads data, or to
        something taken from one (the data-use analysis of
        ``tests/support/data_use.py``, for a cell)."""
        found = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found |= {
                    a.asname or a.name.split(".")[0]
                    for a in node.names
                    if self._reads_data(a.name)
                }
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                for a in node.names:
                    dotted = f"{node.module}.{a.name}"
                    module = dotted if self._module_path(dotted) else node.module
                    if self._reads_data(module):
                        found.add(a.asname or a.name)
        return found

    def _reads_data(self, dotted: str, seen: frozenset[str] = frozenset()) -> bool:
        """Whether importing ``dotted`` reaches a module of ``pbc.data`` that
        reads data, itself or through the ``pbc`` modules it imports."""
        if not _in_package(dotted) or dotted in seen:
            return False
        if dotted == _DATA_PACKAGE or dotted == "pbc":
            return False
        if dotted.startswith(_DATA_PACKAGE + "."):
            return not any(
                dotted == t or dotted.startswith(t + ".") for t in _DATA_TOOLS
            )
        files = self._module_path(dotted)
        if not files:
            return False
        tree = self._tree(files[-1])
        if tree is None:
            return False
        package = list(files[-1].relative_to(self.root / _PACKAGE_ROOT).parent.parts)
        return any(
            self._reads_data(module, seen | {dotted})
            or any(
                self._reads_data(f"{module}.{n}", seen | {dotted})
                for n in names
                if n != "*"
            )
            for module, names in self._imports(tree, package)
        )

    def _lean_for(self, text: str) -> list[Path]:
        front = _front_matter(text)
        modules = (front.get("lesson") or {}).get("lean-modules") or []
        if not isinstance(modules, list) or not all(
            isinstance(m, str) for m in modules
        ):
            raise Unfollowable("lean-modules is not a list of module names")
        return self._lean_files(modules)

    def digest(self, lesson: Path) -> LessonDigest:
        try:
            entries = self.lesson_files(lesson)
        except Unfollowable as error:
            return LessonDigest(None, str(error))
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
            return LessonDigest(None, f"cannot read the lesson: {error}")
        payload = json.dumps(sorted(entries.items()), separators=(",", ":"))
        return LessonDigest(_sha(f"{FORMAT}\n{payload}".encode()))

    def lessons(self) -> list[Path]:
        base = self.root / LESSONS
        return sorted(p.parent for p in base.glob(f"*/*/{PAGE}"))

    def all(self) -> dict[str, LessonDigest]:
        """The digest of every lesson, by the path of its directory."""
        return {self._label(d): self.digest(d) for d in self.lessons()}


def _in_package(dotted: str) -> bool:
    return dotted == "pbc" or dotted.startswith("pbc.")


def _dynamic_names(tree: ast.AST) -> set[str]:
    """The names in ``tree`` that load code or run text as code.

    An import is looked at by every part of its dotted path, so that
    ``import importlib.util as iu`` is a use of ``importlib`` however it is
    bound; a name or an attribute is looked at by its own name.
    """
    found = set()
    for node in ast.walk(tree):
        names: list[str] = []
        if isinstance(node, ast.Name):
            names = [node.id]
        elif isinstance(node, ast.Attribute):
            names = [node.attr]
        elif isinstance(node, ast.alias):
            names = node.name.split(".")
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = node.module.split(".")
        found.update(n for n in names if n in _DYNAMIC)
    return found


def _named(ids: list[str], strings: list[str]) -> set[str]:
    """The datasets whose identifier occurs in one of the strings."""
    text = "\n".join(strings)
    return {i for i in ids if re.search(rf"(?<![\w-]){re.escape(i)}(?![\w-])", text)}


def _names_directory(tree: ast.AST) -> bool:
    return any(
        (isinstance(n, ast.Name) and n.id in _DATA_DIRECTORY_NAMES)
        or (isinstance(n, ast.Attribute) and n.attr in _DATA_DIRECTORY_NAMES)
        for n in ast.walk(tree)
    )


def _reads_directory(tree: ast.AST) -> bool:
    """Whether a module uses a data directory it got from elsewhere (it does
    not define it: the package that defines them hands out no data itself)."""
    return any(
        isinstance(n, ast.Name)
        and isinstance(n.ctx, ast.Load)
        and n.id in _DATA_DIRECTORY_NAMES
        for n in ast.walk(tree)
    )


def _calls_with_unknown(tree: ast.AST, sources: set[str]) -> bool:
    """Whether a cell calls a data reader with an argument that is not a
    literal: the dataset it names may then come from anywhere."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        root = _root(node.func)
        if root not in sources:
            continue
        arguments = [*node.args, *(k.value for k in node.keywords)]
        if not all(_is_literal(a) for a in arguments):
            return True
    return False


def _is_literal(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, ast.Tuple | ast.List | ast.Set):
        return all(_is_literal(e) for e in node.elts)
    if isinstance(node, ast.UnaryOp):
        return _is_literal(node.operand)
    return False


def _strings(tree: ast.AST) -> list[str]:
    return [
        n.value
        for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
    ]


def _check_reads(tree: ast.AST, exported: frozenset[str] = frozenset()) -> None:
    """Fail when a cell reads a file that is not in a known location.

    A path built from literals and from names that ``pbc`` modules export
    (``SAMPLES_DIR``) lies in a known location; anything else does not. A
    reader is recognised by its name, as a function of a module
    (``pandas.read_csv``), a method of a path (``Path.open``) and a name
    (``from numpy import load``). A reader that is not called where it is
    mentioned (``f = pandas.read_csv``) cannot be followed. ``exported`` holds
    the names the other cells of the page import from ``pbc``, which an inline
    expression can use.
    """
    safe = _safe_names(tree, exported)
    called = {id(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
    modules = _module_names(tree)
    for node in ast.walk(tree):
        name = _reader_name(node)
        if name is not None and id(node) not in called and _is_reader_use(node, safe):
            raise Unfollowable(f"a cell refers to {name!r} without calling it")
        if not isinstance(node, ast.Call):
            continue
        name = _reader_name(node.func)
        if name is None:
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in safe - _PATH_CLASSES:
            continue  # a ``pbc`` helper reads its own locations
        if isinstance(func, ast.Attribute):
            root = _root(func.value)
            if root in safe - _PATH_CLASSES and root not in modules:
                # ``SAMPLES_DIR.glob``: the receiver is a known location.
                if not _is_safe_path(func.value, safe):
                    raise Unfollowable("a cell reads a path put together from parts")
                continue
            if root in modules:
                # A function of a module: the path is an argument.
                paths = [*node.args[:1], *(k.value for k in node.keywords)]
            else:
                # A method of a path: the path is the receiver.
                paths = [func.value]
        else:
            paths = [*node.args[:1], *(k.value for k in node.keywords)]
        for path in paths:
            _require_safe_path(path, safe)


def _reader_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name) and node.id in _READERS:
        return node.id
    if isinstance(node, ast.Attribute) and node.attr in _READERS:
        return node.attr
    return None


def _is_reader_use(node: ast.AST, safe: set[str]) -> bool:
    """A reader mentioned, not called, unless it is a ``pbc`` name."""
    if isinstance(node, ast.Name):
        return node.id not in safe
    return isinstance(node, ast.Attribute) and _root(node.value) not in safe


def _root(node: ast.AST) -> str | None:
    """The name an expression starts from: ``a`` of ``a.b(c).d[e]``."""
    while isinstance(node, ast.Attribute | ast.Subscript | ast.Call):
        node = node.value if not isinstance(node, ast.Call) else node.func
    return node.id if isinstance(node, ast.Name) else None


def _module_names(tree: ast.AST) -> set[str]:
    """The names bound to an imported module or to a name taken from one that
    is not part of ``pbc``: their functions take a path as an argument."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {(a.asname or a.name.split(".")[0]) for a in node.names}
            names -= {
                a.asname or a.name.split(".")[0]
                for a in node.names
                if _in_package(a.name)
            }
    return names


_LEXICAL_PATH_METHODS = frozenset(
    {"joinpath", "with_suffix", "with_name", "with_stem", "relative_to", "as_posix"}
)


def _is_safe_path(node: ast.AST, safe: set[str]) -> bool:
    """Whether a path expression lies in a known location."""
    folded = _folded(node)
    if folded is not None:
        return _is_contained(folded)
    if isinstance(node, ast.Constant):
        return False
    if isinstance(node, ast.Name):
        return node.id in safe
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div | ast.Add):
        return _is_safe_path(node.left, safe) and _is_safe_path(node.right, safe)
    if isinstance(node, ast.Attribute):
        # ``.parent`` and ``.parents`` leave the location.
        return node.attr not in {"parent", "parents"} and _is_safe_path(
            node.value, safe
        )
    if isinstance(node, ast.Subscript):
        return _is_safe_path(node.value, safe)
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id in _PATH_CLASSES:
            return all(_is_safe_path(a, safe) for a in node.args) and not node.keywords
        if isinstance(func, ast.Attribute):
            # ``base.joinpath("x")``, ``base.with_suffix(".csv")``: only
            # lexical operations; ``resolve()`` and the like consult the file
            # system and can follow a symlink out of the repository.
            return (
                func.attr in _LEXICAL_PATH_METHODS
                and _is_safe_path(func.value, safe)
                and all(_is_safe_path(a, safe) for a in node.args)
                and not node.keywords
            )
    return False


def _folded(node: ast.AST) -> str | None:
    """The value of a string literal or of literals added together."""
    if isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, str) else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _folded(node.left), _folded(node.right)
        if left is not None and right is not None:
            return left + right
    return None


def _is_contained(text: str) -> bool:
    """Whether a literal path part stays below the place it is joined to:
    not absolute, not home-relative, no ``..`` step."""
    text = text.replace("\\", "/")
    if text.startswith(("/", "~")) or (len(text) > 1 and text[1] == ":"):
        return False
    return ".." not in text.split("/")


def _require_safe_path(node: ast.AST, safe: set[str]) -> None:
    folded = _folded(node)
    if folded is not None and not _is_contained(folded):
        raise Unfollowable(f"a cell reads outside the repository ({folded[:40]})")
    for part in ast.walk(node):
        if isinstance(part, ast.Name) and part.id not in safe:
            raise Unfollowable(f"a cell opens a file by a path from {part.id!r}")
        if isinstance(part, ast.JoinedStr):
            raise Unfollowable("a cell opens a file by a path put together from parts")
    if not _is_safe_path(node, safe):
        raise Unfollowable("a cell opens a file by a path put together from parts")


def _safe_names(tree: ast.AST, exported: frozenset[str] = frozenset()) -> set[str]:
    """Names that stand for a known location: what a ``pbc`` module exports,
    ``Path``, and names assigned a path made of these."""
    names = _pbc_names(tree) | exported
    changed = True
    while changed:
        before = len(names)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign | ast.AnnAssign) and node.value:
                targets = (
                    node.targets if isinstance(node, ast.Assign) else [node.target]
                )
                if _mentions(node.value, names) and _is_safe_path(node.value, names):
                    names |= {t.id for t in targets if isinstance(t, ast.Name)}
            elif isinstance(node, ast.For) and isinstance(node.target, ast.Name):
                if _mentions(node.iter, names) and _is_safe_iterable(node.iter, names):
                    names.add(node.target.id)
        changed = len(names) != before
    return names


def _mentions(node: ast.AST, names: set[str]) -> bool:
    return any(isinstance(n, ast.Name) and n.id in names for n in ast.walk(node))


def _is_safe_iterable(node: ast.AST, safe: set[str]) -> bool:
    """``SAMPLES_DIR.glob("*")``, ``sorted(SAMPLES_DIR.iterdir())``."""
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id in {"sorted", "list", "enumerate"}:
            return all(_is_safe_iterable(a, safe) for a in node.args)
        if isinstance(func, ast.Attribute):
            return _is_safe_path(func.value, safe) and all(
                _is_safe_path(a, safe) for a in node.args
            )
    return _is_safe_path(node, safe)


def _pbc_names(tree: ast.AST) -> set[str]:
    names = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and _in_package(node.module)
        ):
            names |= {a.asname or a.name for a in node.names}
        elif isinstance(node, ast.Import):
            names |= {
                a.asname or a.name.split(".")[0]
                for a in node.names
                if _in_package(a.name)
            }
    return names | _PATH_CLASSES


def _cells(text: str) -> tuple[list[str], list[str]]:
    """The code of the executed cells and the inline expressions of a page."""
    cells: list[str] = []
    prose: list[str] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        match = _FENCE.match(lines[index])
        index += 1
        if not match:
            prose.append(lines[index - 1])
            continue
        indent, fence, language = match.groups()
        body = []
        while index < len(lines) and lines[index].strip() != fence:
            body.append(lines[index].removeprefix(indent))
            index += 1
        index += 1
        if language != "python":
            raise Unfollowable(f"a cell in {language}")
        if any(re.match(r"\s*[%!]", line) for line in body):
            raise Unfollowable("a cell with a magic or shell line")
        cells.append(
            "\n".join(line for line in body if not line.lstrip().startswith("#|"))
        )
    inline = [m.strip() for m in _INLINE.findall("\n".join(prose))]
    return cells, inline


def _front_matter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        raise Unfollowable("the front matter is not closed")
    loaded = yaml.safe_load(text[3:end])
    return loaded if isinstance(loaded, dict) else {}


# What the checks are made of and run on (ADR 014 decision 10).
CHECK_FILES = (
    "scripts/verify.sh",
    "scripts/verify.conf",
    "scripts/build-site.sh",
    "scripts/check-determinism.sh",
    "pyproject.toml",
    "uv.lock",
    ".github/actions/prepare/action.yml",
)
CHECK_DIRECTORIES = ("tests/e2e", "tests/support", "tests/integration")


def check_identity(root: Path = REPOSITORY_ROOT) -> str:
    """One digest over the implementation of the checks that run less often
    with a base. ``tests/e2e/shards.json`` is inside ``tests/e2e``; the
    browser tooling is what the preparation of a runner installs."""
    root = root.resolve()
    files = [root / name for name in CHECK_FILES]
    for name in CHECK_DIRECTORIES:
        files += [p for p in _files_under(root / name) if p.suffix != ".html"]
    entries = []
    for path in files:
        label = path.relative_to(root).as_posix()
        try:
            entries.append((label, _sha(path.read_bytes())))
        except OSError:
            entries.append((label, "missing"))  # a missing file is part of it
    payload = json.dumps(sorted(entries), separators=(",", ":"))
    return _sha(f"{FORMAT}\n{payload}".encode())


def render(root: Path) -> str:
    """The digests of every lesson, and the identity of the checks, as the
    JSON the build writes."""
    digester = Digester(root)
    lessons = {
        path: {"digest": d.value, **({"reason": d.reason} if d.reason else {})}
        for path, d in digester.all().items()
    }
    return (
        json.dumps(
            {"format": FORMAT, "identity": check_identity(root), "lessons": lessons},
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Write the input digest of every lesson."
    )
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument(
        "--out", type=Path, help="file to write (default: standard output)"
    )
    arguments = parser.parse_args(argv)
    text = render(arguments.root)
    if arguments.out:
        arguments.out.parent.mkdir(parents=True, exist_ok=True)
        arguments.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
