from pathlib import Path
from subprocess import call
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


@pytest.fixture
def drinkrc(tmpfile):
    with open(tmpfile, 'w') as f:
        f.write('TARGET="somehost"\n')
        f.write(f'DRINKDIR="relative/path"\n')
    return tmpfile


@pytest.fixture
def tracked_drinkrc_and_drinkdir(drinkrc_and_drinkdir):
    c = Config(drinkrc_and_drinkdir)
    git = ["git", "-C", str(c["DRINKDIR"])]
    call(git + ["init"])
    call(git + ["add", "."])
    call(git + ["commit", "-m", "test"])
    for remote in ["hostA", "hostB", "hostC"]:
        ref = c["DRINKDIR"] / ".git" / "refs" / "remotes" / remote / "master"
        ref.parent.mkdir(parents=True)
        with open(ref, "w") as f:
            f.write("45c00db8f531f6ad6414dd4fa048893dd8095ff2\n")
    return drinkrc_and_drinkdir
