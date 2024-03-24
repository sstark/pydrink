from enum import Enum
from pathlib import Path
from textwrap import dedent
from typing import Optional
import shutil

from pydrink.config import KINDS, BY_TARGET, Config
from pydrink.log import debug, warn, err

GLOBAL_TARGET = "global"


class InvalidKind(Exception):
    '''Raised when an invalid kind is requested or used'''
    pass


class InvalidDrinkObject(Exception):
    '''Raised when a drink object does not look right'''
    pass


class ObjectState(Enum):
    Unmanaged = 1
    ManagedHere = 2
    ManagePending = 3
    ManagedOther = 4


class DrinkObject():
    '''A class to represent drink objects

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
    '''

    def __init__(self, c: Config, p: Path):
        '''Initialize a drink object

        Parameters
        ----------
        p: pathlib.Path
            The path of the file describing the drink object. Must be contained
            in drink repository ("DRINKDIR").

        '''
        self.config: Config = c
        # TODO: check that path is absolute
        # Keep this path as a reminder how the object was referred to when
        # it was created.
        self.p = p
        # This is the path relative to kindDir
        self.relpath: Path
        self.state: Optional[ObjectState] = None
        self.kind: str = ""
        self.target: Optional[str] = None
        self.update_state(c)
        self.check()

    def __str__(self):
        return dedent(f"""\
            DrinkObject: ({self.state})
              p: {self.p}
              relpath: {self.relpath}
              kind: {self.kind}
              target: {self.target}""")

    def check(self):
        if not self.is_in_drinkdir():
            raise InvalidDrinkObject(
                f"{self.p} is not in {self.config['DRINKDIR']}")
        try:
            _ = self.relpath, self.state, self.kind, self.target
        except AttributeError as e:
            raise InvalidDrinkObject(f"DrinkObject is incomplete: {e}")

    def is_in_drinkdir(self) -> bool:
        return self.p.is_relative_to(self.config["DRINKDIR"])

    def detect_kind(self) -> str:
        c = self.config
        for kind in KINDS:
            if self.p.is_relative_to(
                    c.kindDir(kind)) and not self.p.is_relative_to(
                        c["DRINKDIR"]):
                debug(f"{self.p} is inside kinddir {kind}")
                return kind
        return ""

    def detect_target(self) -> str:
        # if not self.is_in_repo()
        # c = self.config
        # for target in c.managedTargets():
        #     if
        return ""

    def update_state(self, c: Config):
        pass

    def get_linkpath(self) -> Optional[Path]:
        '''Return the path that this objects is or should be linked to'''
        if self.target == GLOBAL_TARGET:
            return self.config.kindDir(self.kind) / self.relpath
        elif self.target:
            return self.config.kindDir(
                self.kind) / BY_TARGET / self.target / self.relpath
        else:
            return None

    def get_repopath(self) -> Optional[Path]:
        '''Return the path that this object has or should have inside the repo'''
        if self.target == GLOBAL_TARGET:
            return self.config["DRINKDIR"] / self.kind / self.relpath
        elif self.target:
            return self.config[
                "DRINKDIR"] / BY_TARGET / self.target / self.relpath
        else:
            return None

    def import_object(self):
        if self.state == ObjectState.ManagedHere:
            err(f"{self} is already managed.")
            return
        if self.state == ObjectState.ManagedOther:
            err(f"{self} is already managed in other target.")
            return
        if self.state == ObjectState.ManagePending:
            err(f"{self} is already managed, but not linked yet. Run drink -l."
                )
            return
        if self.state == ObjectState.Unmanaged:
            shutil.copy(str(self.get_linkpath()), str(self.get_repopath()))
