import sys
from pydrink.config import Config, BY_TARGET
from pydrink.git import get_branches, menu, unclean


def test_unclean_repo(tracked_drinkrc_and_drinkdir):
    c = Config(tracked_drinkrc_and_drinkdir)
    assert not unclean(c)
    with open(c["DRINKDIR"] / "bin" / BY_TARGET / "bar" / "obj2", "a") as f:
        f.write("newly added line\n")
    assert unclean(c)


def test_get_branches(tracked_drinkrc_and_drinkdir):
    c = Config(tracked_drinkrc_and_drinkdir)
    branches = sorted(get_branches(c))
    assert branches == ["hostA/master", "hostB/master", "hostC/master"]


def test_git_menu_quit(tracked_drinkrc_and_drinkdir):
    c = Config(tracked_drinkrc_and_drinkdir)
    assert menu(c, lambda _: "1") == 0


def test_git_menu_fetch(tracked_drinkrc_and_drinkdir):
    # We will get a busy loop if we replace input() and are on a tty.
    # So let's pretend we are not on a tty.
    sys.stdin.isatty = lambda: False
    c = Config(tracked_drinkrc_and_drinkdir)
    assert menu(c, lambda _: "2") == 0


def test_git_menu_push(tracked_drinkrc_and_drinkdir):
    sys.stdin.isatty = lambda: False
    c = Config(tracked_drinkrc_and_drinkdir)
    assert menu(c, lambda _: "3") == 0


def test_git_menu_invalid_item(tracked_drinkrc_and_drinkdir):
    sys.stdin.isatty = lambda: False
    c = Config(tracked_drinkrc_and_drinkdir)
    assert menu(c, lambda _: "99") == 99
