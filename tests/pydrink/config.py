from pathlib import Path
from pydrink.config import KINDS, Config
import pytest
import tempfile


@pytest.fixture
def tmppath():
    return Path(tempfile.TemporaryDirectory().name)


@pytest.fixture
def drinkdir(tmppath):
    for kind in KINDS:
        p = (tmppath / kind)
        p.mkdir(parents=True)
    (tmppath / "bin" / "by-target" / "foo").mkdir(parents=True)
    (tmppath / "bin" / "by-target" / "foo" / "obj1").touch()
    (tmppath / "bin" / "obj2").touch()
    (tmppath / "bin" / "obj3").touch()
    (tmppath / "bin" / "by-target" / "bar").mkdir(parents=True)
    (tmppath / "bin" / "by-target" / "bar" / "obj2").touch()
    return tmppath


@pytest.fixture
def drinkrc(drinkdir):
    rcfile = drinkdir / ".drinkrc"
    with open(rcfile, 'w') as f:
        f.write('TARGET="singold"\n')
        f.write(f'DRINKDIR="{drinkdir}"\n')
    return rcfile


def test_drinkrc_can_be_parsed(drinkrc):
    c = Config(drinkrc)
    assert c["TARGET"] == "singold"
    assert c["DRINKDIR"] == f"{drinkrc.parent}"
