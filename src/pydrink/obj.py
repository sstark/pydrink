from enum import Enum
from pathlib import Path
from textwrap import dedent
from typing import Optional
import shutil
import filecmp

from pydrink.config import KINDS, BY_TARGET, Config
from pydrink.log import debug, err

GLOBAL_TARGET = "global"
DOT_PREFIX = "dot"


class InvalidKind(Exception):
    """Raised when an invalid kind is requested or used"""

    pass


class InvalidDrinkObject(Exception):
    """Raised when a drink object does not look right"""

    pass


class ObjectState(Enum):
    Unmanaged = 1
    ManagedHere = 2
    ManagedPending = 3
    ManagedOther = 4


class DrinkObject:
    """A class to represent drink objects

    A drink object can be a "binary", a zsh function or configuration file.

    Description of the different object states
    ------------------------------------------

    Actual drink objects are those that exist in the drink repository. They can
    be already symlinked into place. (ManagedHere)

    Or objects exist in the drink repository and have a symlink operation
    pending, which means they would be linked with the next "drink -l" run.
    (ManagedHerePending)

    A mixed form is an object that is not present on the current system (not
    symlinked), but is a drink object for another target or globally.
    (ManagedOther)

    Target in this context always means a context in which an object should be
    symlinked into the environment, usually but not necessarily a hostname.
    """

    def __init__(self, c: Config, p: Path):
        """Initialize a drink object

        Parameters
        ----------
        p: pathlib.Path
            The path of the file describing the drink object. Must be contained
            in drink repository ("DRINKDIR").

        """
        self.config: Config = c
        # Keep this path as a reminder how the object was referred to when
        # it was created.
        self.p = p
        # This is the path relative to kindDir
        self.relpath: Path
        self.state: Optional[ObjectState] = None
        self.kind: str = ""
        self.target: str = ""
        self.update()
        self.check()

    def __str__(self):
        return dedent(
            f"""\
            DrinkObject: ({self.state})
              p: {self.p}
              relpath: {self.relpath}
              kind: {self.kind}
              target: {self.target}"""
        )

    def check(self):
        if not self.is_in_drinkdir():
            raise InvalidDrinkObject(f"{self.p} is not in {self.config['DRINKDIR']}")
        try:
            _ = self.relpath, self.state, self.kind, self.target
        except AttributeError as e:
            raise InvalidDrinkObject(f"DrinkObject is incomplete: {e}")

    def is_in_drinkdir(self) -> bool:
        return self.p.is_relative_to(self.config["DRINKDIR"])

    def detect_relpath(self) -> Path:
        """Return the part of the object path that is below the
        target node. Target node could be absent.
        """
        c = self.config
        relpath = self.p.relative_to(c.drinkdir)
        debug(f"relpath: {relpath}")
        if relpath.parts[1] == BY_TARGET:
            debug(f"{relpath} has BY_TARGET")
            return Path(*relpath.parts[3:])
        else:
            debug(f"{relpath} is global")
            return Path(*relpath.parts[1:])

    def detect_kind(self) -> str:
        """Return the kind of the object as derived from the path"""
        c = self.config
        kind = self.p.relative_to(c.drinkdir).parts[0]
        if kind in KINDS:
            return kind
        else:
            raise InvalidKind

    def detect_target(self) -> str:
        """Return the target of the object as derived from the path
        If there is no target, return the global target
        """
        c = self.config
        parts = self.p.relative_to(c.drinkdir).parts
        if parts[1] == BY_TARGET:
            target = parts[2]
            debug(f"target is {target}")
            return target
        else:
            return GLOBAL_TARGET

    def detect_state(self) -> ObjectState:
        if self.get_linkpath().is_symlink():
            if self.target == self.config["TARGET"]:
                return ObjectState.ManagedHere
            else:
                return ObjectState.ManagedOther
        else:
            if self.target in (self.config["TARGET"], GLOBAL_TARGET):
                return ObjectState.ManagedPending
            else:
                return ObjectState.ManagedOther

    def update(self):
        if not self.p.is_absolute():
            raise InvalidDrinkObject(f"{self.p} is not absolute")
        # exception for "drink" during transition from zsh drink to pydrink
        if self.p.is_symlink() and self.p.name != "drink":
            raise InvalidDrinkObject(f"{self.p} is a symlink")
        self.relpath = self.detect_relpath()
        self.kind = self.detect_kind()
        self.target = self.detect_target()
        self.state = self.detect_state()

    @staticmethod
    def _dotify(p: Path) -> Path:
        """Return same path, but with all elements prefixed with DOT_PREFIX in
        case they start with a dot"""
        return Path(*[DOT_PREFIX + x if x.startswith(".") else x for x in p.parts])

    @staticmethod
    def _undotify(p: Path) -> Path:
        """Return same path, but with DOT_PREFIX removed drom all elements"""
        return Path(*[x.removeprefix(DOT_PREFIX) for x in p.parts])

    def get_linkpath(self) -> Path:
        """Return the path that this objects is or should be linked to"""
        return self.config.kindDir(self.kind) / self._undotify(self.relpath)

    def get_repopath(self, relative: bool = False) -> Path:
        """Return the path that this object has or should have inside the repo"""
        if self.target == GLOBAL_TARGET:
            if relative:
                return Path(self.kind) / self.relpath
            else:
                return self.config["DRINKDIR"] / self.kind / self.relpath
        else:
            if relative:
                return Path(self.kind) / BY_TARGET / self.target / self.relpath
            else:
                return (
                    self.config["DRINKDIR"]
                    / self.kind
                    / BY_TARGET
                    / self.target
                    / self.relpath
                )

    @classmethod
    def import_object(
        cls, c: Config, relpath: Path, kind: str, target: str
    ) -> "DrinkObject":
        """Create a new drink object by copying it into the repository
        and commit.
        The path must not be inside DRINKDIR.
        """
        if relpath.is_absolute():
            raise InvalidDrinkObject(f"{relpath} is an absolute path")
        debug(f"relpath: {relpath}")
        if target == GLOBAL_TARGET:
            dest_target = Path("")
        else:
            dest_target = Path(BY_TARGET) / target
        src_path = Path.home() / c.kindDir(kind) / relpath
        debug(f"src_path: {src_path}")
        if src_path.is_dir():
            raise InvalidDrinkObject(f"{src_path} is a directory")
        dest_path = c.drinkdir / kind / dest_target / relpath
        dest_path = cls._dotify(dest_path)
        debug(f"dotified dest_path: {dest_path}")
        if dest_path.exists():
            raise InvalidDrinkObject(f"{dest_path} already exists")
        if kind not in KINDS:
            raise InvalidKind
        if not dest_path.parent.exists():
            dest_path.parent.mkdir(parents=True)
        debug(f"copying {src_path} -> {dest_path}")
        shutil.copy(src_path, dest_path)
        # FIXME: here we should probably call git.add_object(newobject) before
        # returning
        return DrinkObject(c, dest_path)

    def link(self, overwrite: bool = False):
        if self.target != self.config["TARGET"] and self.target != GLOBAL_TARGET:
            debug(f"Object target {self.target} is not current nor global target")
            return
        if self.state == ObjectState.ManagedPending:
            fromm = self.get_linkpath().absolute()
            debug(f"creating directory {fromm.parent}")
            fromm.parent.mkdir(parents=True, exist_ok=True)
            to = self.get_repopath().absolute()
            debug(f"linking {fromm} -> {to}")
            if fromm.exists() and overwrite:
                if filecmp.cmp(fromm, to, shallow=False):
                    fromm.unlink()
                else:
                    err(f"{fromm} exists and is different from {to}")
                    return
            fromm.symlink_to(to)
        self.update()
        self.check()
