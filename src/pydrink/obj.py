

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
