from pydrink.config import Config, CONFIG_FILENAME, BY_TARGET
from pydrink.drink import find_drinkrc, get_dangling_links
from pydrink.git import get_tracked_objects
from pathlib import Path
import pytest


def test_get_dangling_links(monkeypatch, tracked_drinkrc_and_drinkdir, fake_home):
    def mock_home():
        return fake_home

    monkeypatch.setattr(Path, "home", mock_home)
    c = Config(tracked_drinkrc_and_drinkdir)
    for obj in get_tracked_objects(c):
        obj.link()
    (Path.home() / "bin" / "dangle1").symlink_to(c.drinkdir / "bin" / "dangle1")
    (Path.home() / ".dangle2").symlink_to(
        c.drinkdir / "conf" / BY_TARGET / "singold" / "dangle2"
    )
    dangle_bin = list(get_dangling_links(c, "bin"))
    assert dangle_bin == [Path.home() / "bin" / "dangle1"]
    dangle_conf = list(get_dangling_links(c, "conf"))
    assert dangle_conf == [Path.home() / ".dangle2"]

    for obj in get_tracked_objects(c):
        assert obj.get_linkpath() not in dangle_bin
        assert obj.get_linkpath() not in dangle_conf


def test_get_dangling_links_not_existing_dir(drinkrc):
    c = Config(drinkrc)
    # reconfigure BINDIR to be in some not existing location
    # This tests the case where somebody has no e. g. zfunc
    # items, so .zfunc was never created.
    c.config["BINDIR"] = "notexisting"
    dangle_notexisting = list(get_dangling_links(c, "bin"))
    # Expected outcome is an empty list and no exception or error
    assert dangle_notexisting == []
    # HACK: WHY has this influence on other tests!?
    c.config["BINDIR"] = "bin"


@pytest.mark.parametrize(
    "present_rcs, found_rc",
    [
        ([Path(".config") / CONFIG_FILENAME], Path(".config") / CONFIG_FILENAME),
        (
            [Path(".config") / CONFIG_FILENAME, Path(f".{CONFIG_FILENAME}")],
            Path(".config") / CONFIG_FILENAME,
        ),
        (
            [Path(".foo") / CONFIG_FILENAME, Path(f".{CONFIG_FILENAME}")],
            Path(".foo") / CONFIG_FILENAME,
        ),
    ],
    ids=["xdg-def", "xdg-def+classic", "xdg-special+classic"],
)
def test_find_drinkrc(monkeypatch, fake_home, present_rcs, found_rc):
    def mock_home():
        return fake_home

    monkeypatch.setattr(Path, "home", mock_home)
    xdg_foo = Path.home() / ".foo"
    xdg_foo.mkdir(parents=True)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(xdg_foo))
    for rc in present_rcs:
        (Path.home() / rc).parent.mkdir(parents=True, exist_ok=True)
        (Path.home() / rc).touch()
    assert find_drinkrc() == Path.home() / found_rc


# def test_tracking_status():
#     pass


# def test_show_untracked_files():
#     pass


# def test_cli():
#     pass
