from pydrink.config import Config, BY_TARGET
from pydrink.git import get_branches, unclean


def test_unclean_repo(tracked_drinkrc_and_drinkdir):
    c = Config(tracked_drinkrc_and_drinkdir)
    with open(c["DRINKDIR"] / "bin" / BY_TARGET / "bar" / "obj2", "a") as f:
        f.write("newly added line\n")
    assert unclean(c)


def test_get_branches(tracked_drinkrc_and_drinkdir):
    c = Config(tracked_drinkrc_and_drinkdir)
    branches = sorted(get_branches(c))
    assert branches == ["hostA/master", "hostB/master", "hostC/master"]
