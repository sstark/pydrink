import sys
from pydrink.config import Config, BY_TARGET
from pydrink.git import get_branches, menu, unclean
import pytest


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


@pytest.mark.parametrize("test_input,expected", [("1", 0), ("2", 0), ("3", 0),
                                                 ("99", 99)])
def test_git_menu_items(tracked_drinkrc_and_drinkdir, test_input, expected):
    # We will get a busy loop if we replace input() and are on a tty.
    # So let's pretend we are not on a tty.
    sys.stdin.isatty = lambda: False
    c = Config(tracked_drinkrc_and_drinkdir)
    assert menu(c, lambda _: test_input) == expected
