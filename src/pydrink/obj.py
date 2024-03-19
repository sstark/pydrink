from enum import Enum
from pathlib import Path
from textwrap import dedent

from pydrink.config import KINDS, BY_TARGET, Config
from pydrink.log import debug

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

    def __init__(self, c: Config, p: Path):
        '''Initialize a drink object

        Parameters
        ----------
        p: pathlib.Path
            The path of the file describing the drink object.

        '''
        # TODO: check that path is absolute
        # Keep this path as a reminder how the object was referred to when
        # it was created.
        self.p = p
        # This is the path relative to kindDir
        self.relpath = None
        self.state = None
        self.kind = None
        self.target = None
        self.updateState(c)

    def __str__(self):
        return dedent(f"""\
            DrinkObject: ({self.state})
              p: {self.p}
              relpath: {self.relpath}
              kind: {self.kind}
              target: {self.target}""")

    def updateState(self, c: Config):
        '''Update state of the drink object from disk'''

        # First check if initial_path ("path") is relevant to drink at all
        # This is the case if:
        #   1) the path is relative to one of $HOME/kindDir
        #      1.1) the path is a symlink
        #         1.1.1) the path is pointing to something in $DRINKDIR
        #            1.1.1.1) pointing to current target
        #                -> ManagedHere
        #                -> set self.relpath
        #            1.1.1.2) pointing to global or other target
        #                -> ManagedOther
        #                -> set self.relpath
        #      1.2) the path is not a symlink
        #         1.2.1) The path has a corresponding object in $DRINKDIR
        #                -> ManagedHerePending
        #                -> set self.relpath
        #         1.2.2) -> Unmanaged
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

        # 1)
        for kind in KINDS:
            # 1.1)
            if self.p.is_relative_to(c.kindDir(kind)):
                debug(f"{self.p} is inside kinddir {kind}")
                # 1.1.1)
                if self.p.is_symlink():
                    debug(f"{self.p} is a symlink")
                    resolved_p = self.p.readlink()
                    # HACK: Make an exception here for "drink" during
                    # transition from zsh drink to python drink.
                    # FIXME: In future versions drink must not be a symlink
                    # inside the repository
                    if resolved_p.is_symlink() and self.p.name != "drink":
                        raise InvalidDrinkObject("No links allowed in kindDirs")
                    debug(f"Check if {self.p} is a directory")
                    if resolved_p.is_dir():
                        # TODO: Implement recursing into directories
                        # which is most relevant for kind "conf"
                        raise InvalidDrinkObject("Directory recursion not implemented")
                    for target in c.managedTargets():
                        if resolved_p == c["DRINKDIR"] / c.kindDir(kind, relative=True) / BY_TARGET / target / self.p.name:
                            self.relpath = self.p.name
                            if target == c["TARGET"]:
                                self.state = ObjectState.ManagedHere
                            else:
                                self.state = ObjectState.ManagedOther
                            self.target = c["TARGET"]
                            self.kind = kind
                            break
                    if resolved_p == c["DRINKDIR"] / c.kindDir(kind, relative=True) / self.p.name:
                        self.relpath = self.p.name
                        self.state = ObjectState.ManagedOther
                        self.target = GLOBAL_TARGET
                        self.kind = kind
                        break


        # 2)
        if self.p.is_relative_to(c["DRINKDIR"]):
            if self.p.is_symlink():
                raise InvalidDrinkObject(
                    "No symlinks allowed inside drink repository")
            self.relpath = self.p.relative_to(c["DRINKDIR"]) 

