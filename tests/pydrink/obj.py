from pathlib import Path
from pydrink.config import Config, BY_TARGET
from pydrink.obj import GLOBAL_TARGET, DrinkObject, ObjectState
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
    "obj_p, kind", [(Path("bin") / BY_TARGET / "foo" / "obj1", "bin"),
                    (Path("bin") / "obj2", "bin"),
                    (Path("conf") / BY_TARGET / "bapf" / "obj4", "conf")])
def test_detect_kind(tracked_drinkrc_and_drinkdir, obj_p, kind):
    c = Config(tracked_drinkrc_and_drinkdir)
    obj = DrinkObject(c, c["DRINKDIR"] / obj_p)
    assert obj.kind == kind


@pytest.mark.parametrize(
    "obj_p, target", [(Path("bin") / BY_TARGET / "foo" / "obj1", "foo"),
                      (Path("bin") / "obj2", GLOBAL_TARGET),
                      (Path("conf") / BY_TARGET / "bapf" / "obj4", "bapf")])
def test_detect_target(tracked_drinkrc_and_drinkdir, obj_p, target):
    c = Config(tracked_drinkrc_and_drinkdir)
    obj = DrinkObject(c, c["DRINKDIR"] / obj_p)
    assert obj.target == target


@pytest.mark.parametrize("obj_p, state", [
    # FIXME: We should rather check if we are on the correct target
    (Path("bin") / BY_TARGET / "singold" / "obj1", ObjectState.ManagedPending),
    (Path("bin") / "obj2", ObjectState.ManagedOther),
    (Path("conf") / BY_TARGET / "bapf" / "obj4", ObjectState.ManagedOther)
])
def test_detect_state(tmppath, monkeypatch, tracked_drinkrc_and_drinkdir,
                      obj_p, state):
    def mock_home():
        return tmppath
    monkeypatch.setattr(Path, "home", mock_home)
    c = Config(tracked_drinkrc_and_drinkdir)
    obj = DrinkObject(c, c["DRINKDIR"] / obj_p)
    obj.link()
    assert obj.state == state


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


@pytest.mark.parametrize("obj_p", [
    Path("bin") / BY_TARGET / "foo" / "obj1",
    Path("bin") / "obj2",
    Path("conf") / BY_TARGET / "bapf" / "obj4"
])
def test_get_repopath(tracked_drinkrc_and_drinkdir, obj_p):
    c = Config(tracked_drinkrc_and_drinkdir)
    obj = DrinkObject(c, c["DRINKDIR"] / obj_p)
    print(obj)
    # We should get out what we put in, except that get_repopath is relative
    assert obj.get_repopath() == obj.p
    assert obj.get_repopath() == c["DRINKDIR"] / obj_p
