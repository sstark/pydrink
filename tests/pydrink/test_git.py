import sys
from pydrink.config import Config, BY_TARGET
from pydrink.git import get_branches, get_changed_files, get_tracked_objects, menu, unclean
import pytest
from pathlib import Path


def test_unclean_repo(tracked_drinkrc_and_drinkdir):
    c = Config(tracked_drinkrc_and_drinkdir)
    assert not unclean(c)
    with open(c["DRINKDIR"] / "bin" / BY_TARGET / "bar" / "obj2", "a") as f:
        f.write("newly added line\n")
    assert unclean(c)


def test_get_branches(tracked_drinkrc_and_drinkdir):
    c = Config(tracked_drinkrc_and_drinkdir)
    mb = c["MASTERBRANCH"]
    branches = sorted(get_branches(c))
    assert branches == [f"hostA/{mb}", f"hostB/{mb}", f"hostC/{mb}"]


def test_get_changed_files(tracked_drinkrc_and_drinkdir):
    c = Config(tracked_drinkrc_and_drinkdir)
    changes_pre = get_changed_files(c)
    assert changes_pre == []
    changed_objects = [(Path("bin") / BY_TARGET / "foo" / "obj1"),
                       (Path("bin") / "obj3"),
                       (Path("conf") / BY_TARGET / "bapf" / ".obj4")]
    for p in changed_objects:
        with open(c['DRINKDIR'] / p, 'w') as f:
            f.write("something")
    changes_post = sorted(get_changed_files(c))
    assert changes_post == sorted(map(str, changed_objects))


@pytest.mark.parametrize("test_input,expected", [("1", 0), ("2", 0), ("3", 0),
                                                 ("99", 99)])
def test_git_menu_items(tracked_drinkrc_and_drinkdir, test_input, expected):
    # We will get a busy loop if we replace input() and are on a tty.
    # So let's pretend we are not on a tty.
    sys.stdin.isatty = lambda: False
    c = Config(tracked_drinkrc_and_drinkdir)
    assert menu(c, lambda _: test_input) == expected


def test_menu_with_changed_files(capsys, tracked_drinkrc_and_drinkdir):
    c = Config(tracked_drinkrc_and_drinkdir)
    changes_pre = get_changed_files(c)
    assert changes_pre == []
    changed_objects = [(Path("bin") / BY_TARGET / "foo" / "obj1"),
                       (Path("bin") / "obj3"),
                       (Path("conf") / BY_TARGET / "bapf" / "obj4")]
    sys.stdin.isatty = lambda: False
    for p in changed_objects:
        with open(c['DRINKDIR'] / p, 'w') as f:
            f.write("something")
    # Here we test that after "git adding" a change from the git menu
    # we get a different result when doing it a second time, because
    # the menu numbering as changed.
    assert menu(c, lambda _: "") == 99
    captured = capsys.readouterr()
    line10 = captured.out.split('\n')[10]
    assert line10 == "10) diff bin/by-target/foo/obj1"
    # Unfortunately doing some more IO and capturing again does not seem to
    # work with pytests capsys. No idea.
    # captured = capsys.readouterr()
    # line10 = captured.out.split('\n')[10]
    # assert line10 == "10) diff bin/obj3"


def test_get_tracked_objects_all(tracked_drinkrc_and_drinkdir):
    c = Config(tracked_drinkrc_and_drinkdir)
    objs = get_tracked_objects(c)
    # The following is a bit fragile because it depends on the order of the
    # output of git ls-files
    assert next(objs).target == "bar"
    assert next(objs).relpath == Path("obj1")
    assert next(objs).relpath == Path("obj3")
    next(objs)
    assert next(objs).kind == "conf"
    assert next(objs, "stop") == "stop"


def test_get_tracked_objects_by_kind_conf(tracked_drinkrc_and_drinkdir):
    c = Config(tracked_drinkrc_and_drinkdir)
    objs = get_tracked_objects(c, kinds={"conf"})
    o = next(objs)
    assert o.kind == "conf"
    assert o.target == "bapf"
    assert next(objs, "stop") == "stop"
