from pathlib import Path
from pydrink.config import Config


def test_drinkrc_can_be_parsed(drinkrc_and_drinkdir):
    c = Config(drinkrc_and_drinkdir)
    assert c["TARGET"] == "singold"
    assert c.drinkdir == drinkrc_and_drinkdir.parent


def test_drinkrc_drinkdir_is_absolute(drinkrc):
    c = Config(drinkrc)
    assert Path(c.drinkdir) == Path.home() / c.drinkdir


def test_managed_targets(drinkrc_and_drinkdir):
    c = Config(drinkrc_and_drinkdir)
    assert c.managedTargets() == {"bapf", "foo", "bar"}


def test_dump_config(drinkrc):
    c = Config(drinkrc)
    c_str_list = sorted(str(c).split("\n"))
    wanted_str_list = [
        "BINDIR=bin",
        "CONFDIR=.",
        "DRINKBASE=base",
        "DRINKBASEURL=",
        "DRINKDIR=relative/path",
        "MASTERBRANCH=main",
        "SUPPORTED_KINDS='bin conf zfunc'",
        "TARGET=somehost",
        "ZFUNCDIR=.zfunc",
    ]
    assert c_str_list == wanted_str_list


def test_kindDir(drinkrc):
    c = Config(drinkrc)
    assert c.kindDir("conf") == Path.home()
    assert c.kindDir("bin") == Path.home() / "bin"
