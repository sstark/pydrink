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
    (Path("bin") / BY_TARGET / "singold" / "obj1", ObjectState.ManagedHere),
    (Path("bin") / "obj2", ObjectState.ManagedOther),
    (Path("conf") / BY_TARGET / "bapf" / "obj4", ObjectState.ManagedPending)
])
def test_detect_state(fake_home, monkeypatch, tracked_drinkrc_and_drinkdir,
                      obj_p, state):
    def mock_home():
        return fake_home
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


def test_import_object(fake_home, monkeypatch, tracked_drinkrc_and_drinkdir):
    def mock_home():
        return fake_home
    monkeypatch.setattr(Path, "home", mock_home)
    c = Config(tracked_drinkrc_and_drinkdir)
    relpath = Path("_stull")
    (fake_home / "zfunc" / relpath).touch()
    obj = DrinkObject.import_object(c, relpath, "zfunc", "global")
    assert obj.state == ObjectState.ManagedPending
    assert obj.relpath == relpath


def test_link(fake_home, monkeypatch, tracked_drinkrc_and_drinkdir):
    def mock_home():
        return fake_home
    monkeypatch.setattr(Path, "home", mock_home)
    c = Config(tracked_drinkrc_and_drinkdir)
    obj = DrinkObject(c, c["DRINKDIR"] / "bin" / "obj3")
    assert obj.state == ObjectState.ManagedPending
    obj.link()
    assert obj.state == ObjectState.ManagedOther
    # second call should do nothing
    obj.link()
    assert obj.state == ObjectState.ManagedOther