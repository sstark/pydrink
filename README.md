pydrink
=======

Very much "WORK IN PROGRESS" Python implemenation of the drink dotfile
management system.

This will maintain files in a git repository and create symlinks to them in
appropriate places in your home directory. You will only need a single
repository for all your different environments. Drink will only symlink the
files that are configured for a target.

A target can be the name of a host, a shared file system or your company name,
whatever makes sense to you in order to group your objects.

Objects are files. Supported kinds are: bin, zfunc, conf. They will be
symlinked into configurable places in your home.

  - 'bin' are scripts or binaries, usually in `~/bin`
  - 'zfuncs' are shell functions, usually in `~/.zfuncs`
  - 'conf' are configuration files in your home, e. g. `~/.vimrc` or
    `~/.config/hypr/hyprland.conf`

The interactive git menu of drink provides a convenient way to manage and
distribute your shell environment.


History
-------

This is yet another dotfile management system. I wrote this originally in zsh
(first commit Mar 14 2008) and use it daily since then.

The zsh version was never published because it is too much entangeled with my
actual shell environment. This rewrite in Python aims to fix that.


Configuration File
------------------

The only configuration file for pydrink is in your home and must be located in
one of `$XDG_CONFIG_HOME/drinkrc`, `$HOME/.config/drinkrc` or `$HOME/.drinkrc`.

Example drinkrc with the minimal settings:

    TARGET=somestring
    DRINKDIR="some/path/to/gitdir"

For TARGET you should chose a value that is unique to the environment in which
you want to use a certain set of pydrink objects. That could be your hostname
or workplace name. Pydrink will only link objects that are either in your
configured target or in the special 'global' target.

DRINKDIR must be a path to the directory where your pydrink object repository
is located. This contains all your files and it will be the place where
symlinked objects point to. If it is a relative path, $HOME will be prepended
to it implicitly.

Values can be put in double quotes. Do not put spaces around the '=' if you
want to use the _drink zsh completion file.


'Destination' vs. 'Target'
--------------------------

For historic reasons the term 'target' in this project is used for the context
in which an object should be linked or not. Usually this is a hostname or the
word 'global'.

The term 'target' as it is normally used for symlinks, refers to the file or
directory, a symlink points to. It could be a symlink too, but usually is a
plain file or directory that is the target of the symbolic link.

To avoid confusion, this project uses the word 'dest' or 'destination' when it
is referring to what is normally a 'target' in symlink world.
