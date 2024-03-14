
from enum import Enum
from pathlib import Path

from pydrink.config import KINDS, Config


class DrinkInvalidKind(Exception):
    '''Raised when an invalid kind is requested or used'''
    pass


class DrinkObjectState(Enum):
    Unmanaged = 1
    ManagedHere = 2
    ManageHerePending = 3
    ManagedOther = 4


class DrinkObject():
    '''A class to represent potential or actual drink objects

    A drink object can be a "binary", a zsh function or configuration file.

    Actual drink objects are those that exist in the drink repository. They can
    be already symlinked into their destination or have a symlink operation
    pending.

    Potential drink objects are those that do not exist in the drink repository, but
    are valid candidates.

    A mixed form is an object that is not present on the current system (not
    symlinked), but is a drink object for another target (another host).

    Target in this context always means a context in which an object should be
    symlinked into the environment, usually but not necessarily a hostname.
    '''

    def __init__(self, kind: str, target: str, path: Path):
        '''Initialize a drink object

        Parameters
        ----------
        kind: str
            Filename to load. Must be a string with the full path.
        target: str
            The object context, usually the hostname.
        path: pathlib.Path
            The path of the file relative to the kind-specific directory.

        '''
        self.kind = kind
        self.target = target
        self.path = path
        self.state = self.detectState()

    @property
    def kind(self):
        return self._kind

    @kind.setter
    def kind(self, val):
        if val not in KINDS:
            raise DrinkInvalidKind
        self._kind = val

    def __str__(self):
        return f"DrinkObject: kind:{self.kind}, target:{self.target}, path:{self.path}"

    def detectState(self, conf: Config) -> DrinkObjectState:
        pass
