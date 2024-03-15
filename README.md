pydrink
=======

Python implemenation of drink dotfile management system

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
