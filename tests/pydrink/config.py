from pathlib import Path
from pydrink.config import KINDS, Config
from pydrink.obj import BY_TARGET
import pytest
import tempfile


@pytest.fixture
def tmppath():
    return Path(tempfile.TemporaryDirectory().name)


@pytest.fixture
def tmpfile():
    return Path(tempfile.NamedTemporaryFile().name)


@pytest.fixture
def drinkdir(tmppath):
    for kind in KINDS:
        (tmppath / kind).mkdir(parents=True)
    (tmppath / "bin" / BY_TARGET / "foo").mkdir(parents=True)
    (tmppath / "bin" / BY_TARGET / "foo" / "obj1").touch()
    (tmppath / "bin" / "obj2").touch()
    (tmppath / "bin" / "obj3").touch()
    (tmppath / "bin" / BY_TARGET / "bar").mkdir(parents=True)
    (tmppath / "bin" / BY_TARGET / "bar" / "obj2").touch()
    (tmppath / "conf" / BY_TARGET / "bapf").mkdir(parents=True)
    (tmppath / "conf" / BY_TARGET / "bapf" / "obj4").touch()
    return tmppath


@pytest.fixture
def drinkrc_and_drinkdir(drinkdir):
    rcfile = drinkdir / ".drinkrc"
    with open(rcfile, 'w') as f:
        f.write('TARGET="singold"\n')
        f.write(f'DRINKDIR="{drinkdir}"\n')
    return rcfile


def test_drinkrc_can_be_parsed(drinkrc_and_drinkdir):
    c = Config(drinkrc_and_drinkdir)
    assert c["TARGET"] == "singold"
    assert c["DRINKDIR"] == f"{drinkrc_and_drinkdir.parent}"


@pytest.fixture
def drinkrc(tmpfile):
    with open(tmpfile, 'w') as f:
        f.write('TARGET="somehost"\n')
        f.write(f'DRINKDIR="relative/path"\n')
    return tmpfile


def test_drinkrc_drinkdir_is_absolute(drinkrc):
    c = Config(drinkrc)
    assert Path(c["DRINKDIR"]) == Path.home() / c["DRINKDIR"]


def test_managed_targets(drinkrc_and_drinkdir):
    c = Config(drinkrc_and_drinkdir)
    assert c.managedTargets() == {'bapf', 'foo', 'bar'}
