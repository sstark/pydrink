import os
from pathlib import Path
from pydrink.log import debug, err, notice
from typing import Any
from configparser import ConfigParser
import platform

CONFIG_FILENAME = "drinkrc"

# Short names to variable names mapping
KINDS = {
    "bin": "BINDIR",
    "zfunc": "ZFUNCDIR",
    "conf": "CONFDIR",
}
# Variable names for ~/.drinkrc and their defaults
VARNAMES = {
    "TARGET": "localhost",
    "DRINKDIR": "git/drink",
    "DRINKBASE": "base",  # The central git remote
    "DRINKBASEURL": "",  # The URL for the central git remote
    "MASTERBRANCH": "main",
    "BINDIR": "bin",
    "ZFUNCDIR": ".zfunc",
    "CONFDIR": ".",
    # used by _drink completion
    "SUPPORTED_KINDS": f"'{' '.join(sorted(KINDS.keys()))}'",
}

# The subdirectory within DRINKDIR in which per target objects are located
BY_TARGET = "by-target"


class Config:
    """The Config class holds the drink configuration and can update its
    default values from a configuration file in drinkrc format.

    This configuration file is in shell format and is sourced several times.
    """

    def __init__(self, f: Path):
        """Initialize Config

        Parameters
        ----------
        f: str
            Filename to load. Must be a string with the full path.

        Returns
        -------
        A configuration object that can be used like a dictionary.

        Examples
        --------
        >>> c = Config(pathlib.Path.home() / '.drinkrc')
        >>> val = c['TARGET']
        """
        self.configFileName = f
        self.config = VARNAMES
        # Override the defaults from config file
        debug(f"Reading configuration from {f}")
        self.sourceConfigFile(f)

    def sourceConfigFile(self, f: Path):
        """Read a drink configuration file and populate the config object"""
        ini = ConfigParser()
        with open(f) as cf:
            # Unfortunately the python ini parser wants a section header
            # although it is not strictly necessary for ini files. We need to
            # add the section header to make configparser happy.
            ini.read_string("[drink]\n" + cf.read())
        for v in VARNAMES:
            try:
                # For backwards compatibility allow values to be in double
                # quotes. (This used to be shell syntax)
                self.config[v] = ini["drink"][v].strip('"')
            except KeyError:
                debug(f"using default value for {v}")

    def __getitem__(self, item: str) -> Any:
        if item == "DRINKDIR":
            if not Path(self.config[item]).is_absolute():
                return Path.home() / self.config[item]
            else:
                return Path(self.config[item])
        return self.config[item]

    @property
    def drinkdir(self) -> Path:
        return self["DRINKDIR"]

    def kindDir(self, kind: str, relative=False) -> Path:
        """Return the symlink directory for a given kind
        with relative=True return relative path (e. g. "bin").
        """
        d = self.config[KINDS[kind]]
        if relative:
            return Path(d)
        return Path.home() / d

    def managedTargets(self):
        # All possible values of target as of now
        dd = Path(self["DRINKDIR"])
        target_glob = "*/" + BY_TARGET + "/*"
        mt = set([x.name for x in dd.glob(target_glob)])
        debug(mt)
        return mt

    def __str__(self) -> str:
        return "\n".join([f"{k}={v}" for k, v in self.config.items()])

    @classmethod
    def create_drinkrc(cls) -> int:
        if xdgch := os.getenv("XDG_CONFIG_HOME"):
            new_drinkrc = Path(xdgch) / CONFIG_FILENAME
        else:
            new_drinkrc = Path.home() / ".config" / CONFIG_FILENAME
        assert not new_drinkrc.exists()
        debug(f"create new drinkrc: {new_drinkrc}")
        try:
            f = open(new_drinkrc, "w")
        except OSError as e:
            err(f"Could not create drinkrc in {new_drinkrc}: {e}")
            return 4
        with f:
            f.write(f"TARGET={platform.node()}\n")
            f.write("DRINKDIR=git/drink\n")
        notice(f"New drinkrc created in {new_drinkrc}.")
        notice("Please review or change the contents and run this command again.")
        return 0
