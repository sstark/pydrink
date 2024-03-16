pydrink
=======

Python implemenation of drink dotfile management system


Configuration File
------------------

The only configuration file for pydrink is in your home and must be either
located in `$XDG_CONFIG_HOME/drinkrc` or, if XDG_CONFIG_HOME is not set,
`$HOME/.drinkrc`.

Example drinkrc with the minimal settings:

    TARGET="somestring"
    DRINKDIR="some/path/to/gitdir"

For TARGET you should chose a value that is unique to the environment in which
you want to use a certain set of pydrink objects. That could be your hostname
or workplace name. Pydrink will only link objects that are either in your
configured target or in the special 'global' target.

DRINKDIR must be a path to the directory where your pydrink object repository
is located. This contains all your files and it will be the place where
symlinked objects point to. If it is a relative path, $HOME will be prepended
to it implicitly.


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
