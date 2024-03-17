
from pydrink.config import Config, BY_TARGET
from pydrink.git import unclean


def test_unclean_repo(tracked_drinkrc_and_drinkdir):
    c = Config(tracked_drinkrc_and_drinkdir)
    with open(c["DRINKDIR"] / "bin" / BY_TARGET / "bar" / "obj2", "a") as f:
        f.write("newly added line\n")
    assert unclean(c)
