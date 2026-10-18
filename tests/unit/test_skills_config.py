"""The skills configuration check (ADR 019 decision 3): each case it must
fail on, with a message that names the skill, and a pass on the repository."""

import hashlib
from datetime import date

import pytest
import yaml

from pbc import skills

PROVENANCE = {
    "name": "sample",
    "kind": "vendored",
    "upstream": "https://example.org/sample, skills/sample/",
    "revision": "0123456789abcdef0123456789abcdef01234567",
    "licence": "MIT",
    "redistribution": "allowed with the notice",
    "audit": "docs/skill-audits/sample.md",
    "assessment": "prose only",
    "reviewed": date(2026, 10, 18),
    "update_policy": "re-audit before a pin moves",
}


def write_skill(root, name="sample", record=None, listed=True, drop=()):
    directory = root / ".agents" / "skills" / name
    (directory / "reference").mkdir(parents=True)
    (directory / "SKILL.md").write_text(f"---\nname: {name}\n---\n\nGuidance.\n")
    (directory / "reference" / "notes.md").write_text("More guidance.\n")
    record = {**(PROVENANCE if record is None else record), "name": name}
    record = {**record, "digest": skills.digest(directory)}
    record = {key: value for key, value in record.items() if key not in drop}
    (directory / "PROVENANCE.yaml").write_text(yaml.safe_dump(record))
    readme = root / ".agents" / "skills" / "README.md"
    text = readme.read_text() if readme.exists() else "# Skills\n\n"
    if listed:
        readme.write_text(text + f"- [{name}]({name}/SKILL.md)\n")
    else:
        readme.write_text(text)
    return directory


@pytest.fixture
def root(tmp_path):
    (tmp_path / "docs" / "skill-audits").mkdir(parents=True)
    (tmp_path / "docs" / "skill-audits" / "sample.md").write_text("# Audit\n")
    (tmp_path / ".agents" / "plans").mkdir(parents=True)
    write_skill(tmp_path)
    return tmp_path


# The two tests of the repository's own skills. Without the directory they
# skip: the check itself then fails and names it (ADR 019: the other checks
# pass without .agents/skills/).
needs_the_skills = pytest.mark.skipif(
    not (skills.REPO_ROOT / skills.SKILLS).is_dir(),
    reason="no .agents/skills/; skills-config reports it",
)


def plan(root, text):
    (root / ".agents" / "plans" / "9-feature.md").write_text(f"# Plan\n\n{text}\n")


@needs_the_skills
def test_the_repository_passes():
    assert skills.check_repository() == []


def test_a_complete_skill_passes(root):
    assert skills.check_repository(root) == []


def test_the_digest_is_the_one_the_shell_command_of_the_readme_prints(root):
    directory = root / ".agents" / "skills" / "sample"
    lines = "".join(
        f"{hashlib.sha256((directory / path).read_bytes()).hexdigest()}  ./{path}\n"
        for path in ("SKILL.md", "reference/notes.md")
    )
    assert skills.digest(directory) == hashlib.sha256(lines.encode()).hexdigest()


@needs_the_skills
def test_the_vendored_copy_has_the_digest_of_the_audited_upstream():
    # docs/skill-audits/frontend-design.md: the upstream directory at dbd4588f.
    directory = skills.REPO_ROOT / ".agents" / "skills" / "frontend-design"
    assert skills.digest(directory) == (
        "180ab393af52fde72c621db7a1236e48c3b6769682961ea8cada4d9fac454d1c"
    )


def test_a_listed_skill_without_its_directory_fails(root):
    readme = root / ".agents" / "skills" / "README.md"
    readme.write_text(readme.read_text() + "- [gone](gone/SKILL.md)\n")
    assert skills.check_repository(root) == [
        "skill gone: listed in .agents/skills/README.md, but its directory is missing"
    ]


def test_a_skill_without_skill_md_fails(root):
    (root / ".agents" / "skills" / "sample" / "SKILL.md").unlink()
    problems = skills.check_repository(root)
    assert "skill sample: no .agents/skills/sample/SKILL.md" in problems


def test_a_skill_md_that_names_another_skill_fails(root):
    directory = write_skill(root, "other")
    (directory / "SKILL.md").write_text("---\nname: sample\n---\n")
    problems = skills.check_repository(root)
    assert "skill other: SKILL.md declares the name 'sample'" in problems


def test_a_directory_the_readme_does_not_list_fails(root):
    write_skill(root, "stray", listed=False)
    assert skills.check_repository(root) == [
        "skill stray: not listed in .agents/skills/README.md"
    ]


def test_a_missing_provenance_record_fails(root):
    (root / ".agents" / "skills" / "sample" / "PROVENANCE.yaml").unlink()
    assert skills.check_repository(root) == [
        "skill sample: no provenance record .agents/skills/sample/PROVENANCE.yaml"
    ]


@pytest.mark.parametrize("field", (*skills.FIELDS, "audit"))
def test_an_incomplete_provenance_record_fails(tmp_path, field):
    (tmp_path / "docs" / "skill-audits").mkdir(parents=True)
    (tmp_path / "docs" / "skill-audits" / "sample.md").write_text("# Audit\n")
    write_skill(tmp_path, drop=(field,))
    problems = skills.check_repository(tmp_path)
    assert any(
        p.startswith("skill sample: .agents/skills/sample/PROVENANCE.yaml lacks")
        and field in p
        for p in problems
    ), problems


def test_an_adapter_without_its_source_material_fails(root):
    write_skill(root, "adapted", record=dict(PROVENANCE, kind="adapter"))
    assert skills.check_repository(root) == [
        "skill adapted: .agents/skills/adapted/PROVENANCE.yaml lacks source_material"
    ]


def test_a_revision_that_is_not_a_commit_fails(root):
    write_skill(root, "branch", record=dict(PROVENANCE, revision="main"))
    assert skills.check_repository(root) == [
        "skill branch: revision 'main' is not a full commit SHA"
    ]


def test_a_changed_file_does_not_match_the_digest(root):
    notes = root / ".agents" / "skills" / "sample" / "reference" / "notes.md"
    notes.write_text("Changed guidance.\n")
    (problem,) = skills.check_repository(root)
    assert problem.startswith(
        "skill sample: the files do not match the recorded digest"
    )


def test_an_added_file_does_not_match_the_digest(root):
    scripts = root / ".agents" / "skills" / "sample" / "scripts"
    scripts.mkdir()
    (scripts / "launcher").write_text("#!/bin/sh\n")
    (problem,) = skills.check_repository(root)
    assert problem.startswith(
        "skill sample: the files do not match the recorded digest"
    )


def test_a_symbolic_link_in_a_skill_fails(root):
    directory = root / ".agents" / "skills" / "sample"
    (directory / "elsewhere.md").symlink_to(
        root / "docs" / "skill-audits" / "sample.md"
    )
    assert "skill sample: sample/elsewhere.md is a symbolic link" in (
        skills.check_repository(root)
    )


def test_a_plan_that_names_an_unknown_skill_fails(root):
    plan(root, "Skills: sample, missing-skill")
    assert skills.check_repository(root) == [
        ".agents/plans/9-feature.md: names the skill missing-skill, which "
        ".agents/skills/ does not have"
    ]


def test_a_plan_that_names_another_revision_fails(root):
    plan(root, "- Skills: sample@fedcba9")
    (problem,) = skills.check_repository(root)
    assert problem.startswith(".agents/plans/9-feature.md: names sample@fedcba9")


def test_a_plan_at_the_recorded_revision_or_digest_passes(root):
    record = yaml.safe_load(
        (root / ".agents" / "skills" / "sample" / "PROVENANCE.yaml").read_text()
    )
    plan(root, f"Skills: `sample@0123456`, sample@{record['digest'][:12]}")
    assert skills.check_repository(root) == []


def test_a_plan_with_no_skill_or_a_quoted_example_passes(root):
    plan(root, "Skills: none (no visual deliverable)\n\n```\nSkills: unknown\n```")
    assert skills.check_repository(root) == []


def test_a_skill_whose_name_starts_with_none_is_checked(root):
    plan(root, "Skills: none-such")
    assert skills.check_repository(root) == [
        ".agents/plans/9-feature.md: names the skill none-such, which "
        ".agents/skills/ does not have"
    ]


def test_a_malformed_skills_line_fails(root):
    plan(root, "Skills: sample for the figure")
    (problem,) = skills.check_repository(root)
    assert "is not 'Skills: <name>[@<revision>], ...'" in problem


def test_without_the_directory_the_check_fails(tmp_path):
    assert skills.check_repository(tmp_path) == [".agents/skills/ does not exist"]


def test_the_command_reports_and_fails(root, monkeypatch, capsys):
    (root / ".agents" / "skills" / "sample" / "PROVENANCE.yaml").unlink()
    monkeypatch.setattr(skills, "REPO_ROOT", root)
    monkeypatch.setattr(skills.check_repository, "__defaults__", (root,))
    assert skills.main([]) == 1
    assert (
        "skills-config: skill sample: no provenance record" in capsys.readouterr().err
    )
