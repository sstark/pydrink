pydrink
=======

Very much "WORK IN PROGRESS" Python implemenation of the drink dotfile
management system.

This will maintain files in a git repository and create symlinks to them in
appropriate places in your home directory. You will only need a single
repository for all your different environments. Drink will only symlink the
files that are configured for a _target_.

The **interactive git menu** of drink provides a convenient way to manage and
distribute your shell environment. Using the git menu you can see which of your
tracked files have changed and quickly decide to keep or discard those changes.

With the drink git menu you can use the distributed content tracking of git
without having to learn the git command line.

A **colorful command line interface** is used to interact with the user.


Audience
--------

This program is for people who:

  - want to have a tidy environment
  - want to share settings and scripts between different locations
  - want to use a central git repository as a distribution base
  - like command line interfaces
  - who are not using one of the thousand similar programs already
    and, for some reason, found pydrink and are convinced by a concept that the
    author has been using daily for 16 years on ever changing systems (mostly
    Linux, but also Mac and Windows), when it was just a simple zsh script
  - are not afraid of symlinks


Concepts
--------

A _target_ can be the name of a host, a shared file system or your company
name, whatever makes sense to you in order to group your objects. The author
uses a different target for each home directory. At work this is the same for
all hosts, while at home this is different for all hosts.

Objects are files. Supported kinds are: bin, zfunc, conf. They will be
symlinked into configurable places in your home.

  - 'bin' are scripts or binaries, usually in `~/bin`
  - 'zfuncs' are shell functions, usually in `~/.zfuncs`
  - 'conf' are configuration files in your home, e. g. `~/.vimrc` or
    `~/.config/hypr/hyprland.conf`

Kinds are the different types of objects, currently "bin", "zfunc" and "conf".
A kind has a specific storage location in the drink repository, and it has a
dedicated place where it will be linked to in the users home directory.

(The _pydrink_ code is structured such that new kinds could be easily added. For
example, somebody might want to add a kind for storing bash aliases. Currently
this needs changes to the code, but with modest effort.)


History
-------

This is yet another dotfile management system. I wrote this originally in zsh
(first commit Mar 14 2008) and use it daily since then.

The zsh version was never published because it is too much entangeled with my
actual shell environment. This rewrite in Python aims to fix that.


Configuration File
------------------

The only configuration file for _pydrink_ is in your home and must be located in
one of `$XDG_CONFIG_HOME/drinkrc`, `$HOME/.config/drinkrc` or `$HOME/.drinkrc`.

Example drinkrc with the minimal settings:

    TARGET=somestring
    DRINKDIR="some/path/to/gitdir"

For TARGET you should chose a value that is unique to the environment in which
you want to use a certain set of _pydrink_ objects. That could be your hostname
or workplace name. _Pydrink_ will only link objects that are either in your
configured target or in the special 'global' target.

DRINKDIR must be a path to the directory where your _pydrink_ object repository
is located. This contains all your files and it will be the place where
symlinked objects point to. If it is a relative path, $HOME will be prepended
to it implicitly.

Values can be put in double quotes. Do not put spaces around the '=' if you
want to use the _drink zsh completion file.

For historical reasons, configuration keywords (e. g. "TARGET") are in upper
case. This might change in the future for a more modern look, but has low
priority.


Shell Completion
----------------

When importing objects, shell completion is extremely helpful when using drink.
For zsh, a completion file is provided (**_drink**). Just drop that somewhere in
your fpath and enjoy. Of course import it into your drink repository.


'Destination' vs. 'Target'
--------------------------

The term 'target' in this project is used for the context in which an object
should be linked or not. Usually this is a hostname or the word 'global'.

The term 'target' as it is normally used for symlinks, refers to the file or
directory, a symlink points to. It could be a symlink too, but usually is a
plain file or directory that is the target of the symbolic link.

To avoid confusion, this project uses the word 'dest' or 'destination' when it
is referring to what is normally a 'target' in symlink world.


Development
-----------

_pydrink_ tries to use modern Python technology:

  - Dependencies and packaging are managed with **poetry**.

  - Typing hints are used and checked with **mypy**.

  - A **Makefile** (the author could not find a pythonic alternative that is not
    completely over the top for the task) offers targets for typical
    development tasks like testing, cleaning, running debugpy.

  - Tests should be provided for all functionalities through **pytest**.

Enter shell inside development environment:

    make shell

Running tests:

    make test

Typecheck:

    make typecheck

Both:

    make

Verbose:

    make VERBOSE=1

Run a debugpy server, suitable for connecting with e. g. nvim-dap:

    make debug OPTS="-s -d"

Bootstrap:

    git clone https://github.com/sstark/pydrink
    cd pydrink
    <distro-specific-tool> install pipx
    pipx install poetry
    poetry shell
    poetry update
    poetry install
    make
