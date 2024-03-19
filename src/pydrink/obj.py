from enum import Enum
from pathlib import Path
from textwrap import dedent

from pydrink.config import KINDS, BY_TARGET, Config
from pydrink.log import debug

GLOBAL_TARGET = "global"


class InvalidKind(Exception):
    '''Raised when an invalid kind is requested or used'''
    pass


class ObjectState(Enum):
    Unmanaged = 1
    ManagedHere = 2
    ManageHerePending = 3
    ManagedOther = 4


class DrinkObject():
    '''A class to represent potential or actual drink objects

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

    Potential drink objects are those that do not exist in the drink repository, but
    are valid candidates. (Unmanaged)

    Target in this context always means a context in which an object should be
    symlinked into the environment, usually but not necessarily a hostname.
    '''

    def __init__(self, c: Config, path: Path):
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
        # TODO: check that path is absolute
        # Keep this path as a reminder how the object was referred to when
        # it was created.
        self.initial_path = path
        # This is the path relative to kindDir
        self.relpath = None
        self.state = None
        self.kind = None
        self.target = None
        self.updateState(c)

    def __str__(self):
        return dedent(f"""\
            DrinkObject: ({self.state})
              initial_path: {self.initial_path}
              relpath: {self.relpath}"
              kind: {self.kind}
              target: {self.target}""")

    def updateState(self, c: Config):
        '''Update state of the drink object from disk'''

        # First check if the path is relevant to drink at all
        # This is the case if:
        #   1) the path is relative to one of $HOME/kindDir
        #      1.1) the path is not a symlink
        #         1.1.1) The path has a corresponding object in $DRINKDIR
        #                -> ManagedHerePending
        #                -> set self.relpath
        #         1.1.2) -> Unmanaged
        #      1.2) the path is a symlink
        #         1.2.1) the path is pointing to something in $DRINKDIR
        #            1.2.1.1) pointing to current target
        #                -> ManagedHere
        #                -> set self.relpath
        #            1.2.1.2) pointing to global or other target
        #                -> ManagedOther
        #                -> set self.relpath
        #   2) the path is relative to $DRINKDIR. It *must* not be a symlink
        #     -> Set self.relpath
        #     -> Generate the correct symlink based on kind and target information
        #     2.1) If symlink exists:
        #                -> ManagedHere
        #     2.2) If symlink does not exists:
        #                -> ManagedHerePending
        #   3) the path is neither relative to any $HOME/kindDir nor $DRINKDIR
        #                -> Unmanaged
        #                -> return Error
        pass
