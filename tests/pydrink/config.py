from pathlib import Path
from pydrink.config import Config


def test_drinkrc_can_be_parsed(drinkrc_and_drinkdir):
    c = Config(drinkrc_and_drinkdir)
    assert c["TARGET"] == "singold"
    assert c["DRINKDIR"] == drinkrc_and_drinkdir.parent


def test_drinkrc_drinkdir_is_absolute(drinkrc):
    c = Config(drinkrc)
    assert Path(c["DRINKDIR"]) == Path.home() / c["DRINKDIR"]


def test_managed_targets(drinkrc_and_drinkdir):
    c = Config(drinkrc_and_drinkdir)
    assert c.managedTargets() == {'bapf', 'foo', 'bar'}
