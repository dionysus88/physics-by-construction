"""The skills configuration check (ADR 019 decision 3, F122).

``uv run python -m pbc.skills`` is a required verification check. It is the
one check that reads ``.agents/skills/``, and it reads the skills as data to
validate, never as instructions: every skill the README of the directory
lists has a directory, and every directory is listed; each has a ``SKILL.md``
that names it and a provenance record with the required fields whose digest
matches the files; and every skill a feature plan under ``.agents/plans/``
names exists, at the revision the plan gives. ``--digest <directory>`` prints
the digest of a skill directory, for the record of a moved pin.
"""

import hashlib
import re
import sys
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS = Path(".agents") / "skills"
DIR = SKILLS.as_posix()
PLANS = Path(".agents") / "plans"
README = "README.md"
SKILL = "SKILL.md"
PROVENANCE = "PROVENANCE.yaml"
# Written by the macOS Finder; never tracked (.gitignore), never a skill file.
IGNORED = {".DS_Store"}

KINDS = ("vendored", "adapter", "project")
FIELDS = (
    "name", "kind", "upstream", "revision", "licence", "redistribution",
    "assessment", "reviewed", "update_policy", "digest",
)  # fmt: skip
# Fields only some kinds need: a third-party skill has its audit, an adapter
# names the source material it carries or references.
KIND_FIELDS = {
    "vendored": ("audit",),
    "adapter": ("audit", "source_material"),
    "project": (),
}
COMMIT = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")
NAME = re.compile(r"[a-z0-9][a-z0-9-]*")
# A plan names skills on a line 'Skills: <name>[@<revision>], ...' or says
# 'Skills: none (<reason>)'.
SKILLS_LINE = re.compile(r"^\s*(?:[-*]\s+)?(?:\*\*)?Skills:(?:\*\*)?\s*(.*)$")
NO_SKILL = re.compile(r"none(?![a-z0-9-])", re.IGNORECASE)
PLAN_ITEM = re.compile(r"([a-z0-9][a-z0-9-]*)(?:@([0-9a-f]{7,64}))?")
LISTED = re.compile(r"\]\(([^)/]+)/SKILL\.md\)")


def files_of(directory: Path) -> list[Path]:
    """The files of a skill directory that its digest covers: all but the
    provenance record beside SKILL.md."""
    return [
        path
        for path in directory.rglob("*")
        if path.is_file()
        and path.name not in IGNORED
        and path.relative_to(directory).as_posix() != PROVENANCE
    ]


def digest(directory: Path) -> str:
    """SHA-256 of '<sha256>  ./<path>' per file, sorted by path: what
    ``find . -type f ! -name PROVENANCE.yaml -print0 | LC_ALL=C sort -z |
    xargs -0 shasum -a 256 | shasum -a 256`` prints in the directory."""
    lines = []
    for path in files_of(directory):
        relative = path.relative_to(directory).as_posix()
        lines.append((relative, hashlib.sha256(path.read_bytes()).hexdigest()))
    listing = "".join(
        f"{sha}  ./{relative}\n"
        for relative, sha in sorted(lines, key=lambda line: line[0].encode())
    )
    return hashlib.sha256(listing.encode()).hexdigest()


def front_matter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end < 0:
        return {}
    try:
        data = yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def check_provenance(root: Path, name: str, directory: Path) -> tuple[list[str], dict]:
    path = directory / PROVENANCE
    where = f"{DIR}/{name}/{PROVENANCE}"
    if not path.is_file():
        return [f"skill {name}: no provenance record {where}"], {}
    try:
        record = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        return [f"skill {name}: {where} is not valid YAML ({error})"], {}
    if not isinstance(record, dict):
        return [f"skill {name}: {where} is not a mapping of fields"], {}
    out = []
    kind = record.get("kind")
    if kind not in KINDS:
        out.append(f"skill {name}: kind {kind!r} in {where} is not one of {KINDS}")
    required = FIELDS + KIND_FIELDS.get(kind, ())
    missing = [field for field in required if record.get(field) in (None, "", [])]
    if missing:
        out.append(f"skill {name}: {where} lacks {', '.join(missing)}")
    if record.get("name") not in (None, name):
        out.append(f"skill {name}: {where} names the skill {record['name']!r}")
    revision = str(record.get("revision", ""))
    if kind in ("vendored", "adapter") and revision and not COMMIT.fullmatch(revision):
        out.append(f"skill {name}: revision {revision!r} is not a full commit SHA")
    if kind == "project" and revision and revision != "none":
        out.append(f"skill {name}: a project-owned skill has the revision 'none'")
    reviewed = record.get("reviewed")
    if reviewed and not isinstance(reviewed, date):
        out.append(f"skill {name}: reviewed {reviewed!r} is not a date (YYYY-MM-DD)")
    audit = record.get("audit")
    if audit and not (root / str(audit)).is_file():
        out.append(f"skill {name}: the audit {audit} does not exist")
    recorded = str(record.get("digest", ""))
    if recorded:
        actual = digest(directory)
        if not DIGEST.fullmatch(recorded):
            out.append(f"skill {name}: digest {recorded!r} is not a SHA-256")
        elif recorded != actual:
            out.append(
                f"skill {name}: the files do not match the recorded digest "
                f"(recorded {recorded}, found {actual}); a changed copy needs a "
                "re-audit and a new record"
            )
    return out, record


def check_skill(root: Path, name: str, directory: Path) -> tuple[list[str], dict]:
    out = []
    if not NAME.fullmatch(name):
        out.append(
            f"skill {name}: the directory name is not lowercase letters, digits, '-'"
        )
    links = [p for p in [directory, *directory.rglob("*")] if p.is_symlink()]
    for link in links:
        out.append(
            f"skill {name}: {link.relative_to(directory.parent)} is a symbolic link"
        )
    if links:
        return out, {}
    skill = directory / SKILL
    if not skill.is_file():
        out.append(f"skill {name}: no {DIR}/{name}/{SKILL}")
    else:
        declared = front_matter(skill.read_text(encoding="utf-8")).get("name")
        if declared != name:
            out.append(f"skill {name}: {SKILL} declares the name {declared!r}")
    problems, record = check_provenance(root, name, directory)
    return out + problems, record


def plan_references(text: str) -> list[tuple[str, str | None]] | str:
    """The skills a plan names, or the malformed line."""
    names = []
    fenced = False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        match = None if fenced else SKILLS_LINE.match(line)
        if not match:
            continue
        value = match.group(1).strip()
        if NO_SKILL.match(value):
            continue
        for item in value.split(","):
            item = item.strip().strip("`")
            parsed = PLAN_ITEM.fullmatch(item)
            if not parsed:
                return line.strip()
            names.append((parsed.group(1), parsed.group(2)))
    return names


def check_plans(root: Path, records: dict[str, dict]) -> list[str]:
    out = []
    for plan in sorted((root / PLANS).glob("*.md")):
        where = plan.relative_to(root).as_posix()
        references = plan_references(plan.read_text(encoding="utf-8"))
        if isinstance(references, str):
            out.append(
                f"{where}: '{references}' is not 'Skills: <name>[@<revision>], ...' "
                "or 'Skills: none (<reason>)'"
            )
            continue
        for name, revision in references:
            if name not in records:
                out.append(
                    f"{where}: names the skill {name}, which {DIR}/ does not have"
                )
                continue
            record = records[name]
            pins = (str(record.get("revision", "")), str(record.get("digest", "")))
            if revision and not any(pin.startswith(revision) for pin in pins):
                out.append(
                    f"{where}: names {name}@{revision}, but {name} is at revision "
                    f"{pins[0]} with digest {pins[1]}"
                )
    return out


def check_repository(root: Path = REPO_ROOT) -> list[str]:
    skills = root / SKILLS
    if not skills.is_dir():
        return [f"{DIR}/ does not exist"]
    out = []
    readme = skills / README
    listed = set()
    if not readme.is_file():
        out.append(f"{DIR}/{README} does not exist; it lists the skills")
    else:
        listed = set(LISTED.findall(readme.read_text(encoding="utf-8")))
    records = {}
    for entry in sorted(skills.iterdir()):
        if entry.name == README or entry.name in IGNORED:
            continue
        if entry.is_symlink() or not entry.is_dir():
            out.append(f"{DIR}/{entry.name} is not a skill directory")
            continue
        problems, record = check_skill(root, entry.name, entry)
        out += problems
        records[entry.name] = record
        if readme.is_file() and entry.name not in listed:
            out.append(f"skill {entry.name}: not listed in {DIR}/{README}")
    for name in sorted(listed - set(records)):
        out.append(
            f"skill {name}: listed in {DIR}/{README}, but its directory is missing"
        )
    return out + check_plans(root, records)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["--digest"] and len(argv) == 2:
        print(digest(Path(argv[1])))
        return 0
    if argv:
        print(
            "Usage: python -m pbc.skills [--digest <skill directory>]", file=sys.stderr
        )
        return 2
    problems = check_repository()
    for problem in problems:
        print(f"skills-config: {problem}", file=sys.stderr)
    if problems:
        return 1
    count = sum(1 for p in (REPO_ROOT / SKILLS).iterdir() if p.is_dir())
    print(f"skills-config: {count} skills, each with its provenance and digest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
