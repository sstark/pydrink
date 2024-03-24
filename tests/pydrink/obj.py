from pathlib import Path
from pydrink.config import Config, BY_TARGET
from pydrink.obj import DrinkObject
import pytest


@pytest.mark.parametrize(
    "obj_p, relpath",
    [(Path("bin") / BY_TARGET / "foo" / "obj1", Path("obj1")),
     (Path("bin") / "obj2", Path("obj2")),
     (Path("conf") / BY_TARGET / "bapf" / "obj4", Path("obj4"))])
def test_detect_relpath(tracked_drinkrc_and_drinkdir, obj_p, relpath):
    c = Config(tracked_drinkrc_and_drinkdir)
    obj = DrinkObject(c, c["DRINKDIR"] / obj_p)
    assert obj.relpath == relpath


@pytest.mark.parametrize(
    "obj_p, kind",
    [(Path("bin") / BY_TARGET / "foo" / "obj1", "bin"),
     (Path("bin") / "obj2", "bin"),
     (Path("conf") / BY_TARGET / "bapf" / "obj4", "conf")])
def test_detect_kind(tracked_drinkrc_and_drinkdir, obj_p, kind):
    c = Config(tracked_drinkrc_and_drinkdir)
    obj = DrinkObject(c, c["DRINKDIR"] / obj_p)
    assert obj.kind == kind


def test_detect_target():
    pass


def test_detect_state():
    pass


@pytest.mark.parametrize(
    "obj_p, str_p", [(Path("bin") / BY_TARGET / "foo" / "obj1",
                      str(Path.home() / "bin" / "obj1")),
                     (Path("bin") / "obj2", str(Path.home() / "bin" / "obj2")),
                     (Path("conf") / BY_TARGET / "bapf" / "obj4",
                      str(Path.home() / "." / "obj4"))])
def test_get_linkpath(tracked_drinkrc_and_drinkdir, obj_p, str_p):
    c = Config(tracked_drinkrc_and_drinkdir)
    obj = DrinkObject(c, c["DRINKDIR"] / obj_p)
    print(obj)
    assert str(obj.get_linkpath()) == str(str_p)


def test_get_repopath():
    pass
