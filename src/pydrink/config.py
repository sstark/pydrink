
from subprocess import run, CalledProcessError
from pydrink.log import err

# Variable names for ~/.drinkrc and their defaults
VARNAMES = {
    "TARGET":       "localhost",    # FIXME: Use hostname
    "DRINKDIR":     "git/drink",    # A directory in $HOME
    "DRINKBASE":    "base",         # The central git remote
    "MASTERBRANCH":  "master",
    "BINDIR":       "bin",
    "ZFUNCDIR":     ".zfunc",
    "CONFDIR":      ".",
}

# Short names to variable names mapping
KINDS = {
    "bin":      "BINDIR",
    "zfunc":    "ZFUNCDIR",
    "conf":     "CONFDIR",
}


class Config():
    '''The Config class holds the drink configuration and can update its
    default values from a configuration file in drinkrc format.

    This configuration file is in shell format and is sourced several times.
    '''

    def __init__(self, f: str):
        '''Initialize Config

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
        '''
        self.configFileName = f
        self.config = VARNAMES
        # Override the defaults from config file
        self.sourceConfigFile(f)

    def sourceConfigFile(self, f: str):
        for v in VARNAMES:
            try:
                # Yes, this is silly and sources the config file for every variable.
                # The assumption is that it is very cheap, cheaper than importing
                # and using something like the dotenv module.
                # It is also close to the original shell based implementation
                # that was simply sourcing the file too.
                result = run(f"source {f} && echo -n ${v}",
                             shell=True, capture_output=True, text=True)
                result.check_returncode()
                if result.stdout:
                    self.config[v] = result.stdout
            except CalledProcessError as e:
                err(f"{e.returncode}\n{result.stderr}")

    def __getitem__(self, item: str) -> str:
        return self.config[item]

    def __str__(self) -> str:
        return str(self.config)
