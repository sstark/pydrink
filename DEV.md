
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

  - Dependencies and packaging are managed with **uv**.

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

Bootstrap development environment:

    <distro-specific-tool> install uv
    git clone https://github.com/sstark/pydrink
    cd pydrink
    make
