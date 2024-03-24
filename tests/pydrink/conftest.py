from pathlib import Path
from subprocess import call
from pydrink.config import KINDS, Config
from pydrink.obj import BY_TARGET
import pytest
import tempfile
from shutil import rmtree


@pytest.fixture
def tmppath():
    p = Path(tempfile.TemporaryDirectory().name)
    yield p
    rmtree(p)


@pytest.fixture
def base_repo_path():
    p = Path(tempfile.TemporaryDirectory().name)
    yield p
    rmtree(p)


@pytest.fixture
def tmpfile():
    p = Path(tempfile.NamedTemporaryFile().name)
    yield p
    p.unlink()


@pytest.fixture
def drinkdir(tmppath):
    for kind in KINDS:
        (tmppath / kind).mkdir(parents=True)
    (tmppath / "bin" / BY_TARGET / "foo").mkdir(parents=True)
    (tmppath / "bin" / BY_TARGET / "foo" / "obj1").touch()
    (tmppath / "bin" / "objx").touch()
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
def git_base_repo(base_repo_path):
    base_repo_path.mkdir(parents=True)
    call(["git", "-C", base_repo_path, "init", "--bare"])
    return base_repo_path


@pytest.fixture
def tracked_drinkrc_and_drinkdir(drinkrc_and_drinkdir, git_base_repo):
    c = Config(drinkrc_and_drinkdir)
    git = ["git", "-C", str(c["DRINKDIR"])]
    call(git + ["init", "-b", c["MASTERBRANCH"]])
    call(git + ["add", "."])
    call(git + ["commit", "-m", "test"])
    for remote in ["hostA", "hostB", "hostC"]:
        ref = c["DRINKDIR"] / ".git" / "refs" / "remotes" / remote / c["MASTERBRANCH"]
        ref.parent.mkdir(parents=True)
        with open(ref, "w") as f:
            f.write("060c2e38b7147abbc8279f90e06d122aaaa72bad\n")
    call(git + ["config", "remote.base.url", str(git_base_repo)])
    call(git + [
        "config", "remote.base.push",
        f"+refs/heads/*:refs/remotes/{c['TARGET']}/*"
    ])
    call(git + [
        "config",
        "remote.base.fetch",
        f"+refs/remotes/*/{c['MASTERBRANCH']}:refs/remotes/*/{c['MASTERBRANCH']}",
    ])
    return drinkrc_and_drinkdir
