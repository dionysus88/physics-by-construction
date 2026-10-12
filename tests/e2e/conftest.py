"""The built site, served as GitHub Pages serves it."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from support import shards
from support.paths import BUILT_SITE, REPO_ROOT, SITE_SOURCE
from support.site_server import SiteServer, configured_base_path


@pytest.fixture(scope="session")
def site_dir(request: pytest.FixtureRequest) -> Path:
    directory = Path(request.config.getoption("--site-dir") or BUILT_SITE)
    if not (directory / "index.html").is_file():
        # A missing site is a failure, never a skip: these checks are required.
        pytest.fail(
            f"no built site in {directory}; run ./scripts/build-site.sh first",
            pytrace=False,
        )
    return directory


@pytest.fixture(scope="session")
def server(site_dir: Path) -> Iterator[SiteServer]:
    with SiteServer(site_dir, configured_base_path(SITE_SOURCE)) as server:
        yield server


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Keep the part of each test file that --shard asks for."""
    option = config.getoption("--shard")
    if option is None:
        return
    here = Path(__file__).parent
    by_file: dict[str, list[pytest.Item]] = {}
    for item in items:
        if here in item.path.parents:
            by_file.setdefault(item.path.relative_to(REPO_ROOT).as_posix(), []).append(
                item
            )
    try:
        part, parts = shards.parse(option)
        table = shards.table()
        left_out: list[pytest.Item] = []
        for file, tests in by_file.items():
            names = [getattr(test, "originalname", None) or test.name for test in tests]
            known = [name for name in vars(tests[0].module) if name.startswith("test")]
            numbers = shards.part_of(file, names, table, parts, known)
            left_out += [t for t, n in zip(tests, numbers, strict=True) if n != part]
    except shards.ShardError as error:
        raise pytest.UsageError(str(error)) from None
    if left_out:
        gone = set(left_out)
        config.hook.pytest_deselected(items=left_out)
        items[:] = [item for item in items if item not in gone]
