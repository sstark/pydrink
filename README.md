pydrink
=======

Python implemenation of the *drink* dotfile management system.

This will maintain files in a git repository and create symlinks to them in
appropriate places in your home directory. You will only need a single
repository for all your different environments. Drink will only symlink the
files that are configured for a _target_.

The **interactive git menu** of drink provides a convenient way to manage and
distribute your shell environment. Using the git menu you can see which of your
tracked files have changed and quickly decide to keep or discard those changes.

A **colorful command line interface** is used to interact with the user.

With the drink git menu you can use the distributed content tracking of git
without having to learn the git command line:

![drink-menu](https://github.com/sstark/pydrink/assets/837918/b87a6b52-88a4-4df3-b4a9-1c6604705425)


Audience
--------

This program is for people who:

  - want to have a tidy environment
  - want to stay in control of their configuration files
  - want to share settings and scripts between different locations
  - want to use a central git repository as a distribution base
  - like command line interfaces
  - are not using one of the thousand similar programs already and, for some
    reason, found pydrink and are convinced by a concept that the author has
    been using daily for 16 years on ever changing systems (mostly Linux, but
    also Mac and Windows), when it was just a simple zsh script
  - are not afraid of many symlinks in their home directory


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


Interface
---------

Screenshot of the `drink --help` output:

![drink-help](https://github.com/sstark/pydrink/assets/837918/11d8f0fa-4892-4113-b012-3bfb75cca3be)


Getting Started
----------------

If you have not used drink before, you need to create a configuration file
and a repository. For both, drink offers you some assistance:

     $ drink -b
     New drinkrc created in /home/user/.config/drinkrc.
     Please review or change the contents and run this command again.

Now you can open `drinkrc` and customize it before proceeding. See next chapter
for details (and then jump back here). Most importantly you will want to make
at least one of these changes to it before proceeding:

  - Add a **DRINKBASEURL** parameter to it.
  - If you have a shared home directory (e. g. NFS) and your drink repository
    is located on it, you likely want to adjust your **TARGET** parameter to
    not use the hostname, but some broader term.
  - Adjust the location where your drink repository will be created. For that,
    change to **DRINKDIR** parameter to point to some (not yet existing)
    directory. This can be relative to your home.

If you are happy with your `drinkrc`, run `drink -b` again:

    $ drink -b
    Configuration found in /home/user/.config/drinkrc, but the configured git repository does not exist yet.
    Initializing git repository in /home/user/git/drink
    Initialized empty Git repository in /home/user/git/drink/.git/
    A drink repository has been created.
    Configuring git remote.
    Now you should be able to automerge from all remotes:

      drink -g <<<4

    And add all (missing) symlinks:

      drink -lv

At this point we have a fully operable drink setup.

Above process needs to be repeated in all locations where you want to use
drink. This does not apply to locations sharing your home directory.


Configuration File
------------------

The only configuration file for _pydrink_ is in your home and must be located in
one of `$XDG_CONFIG_HOME/drinkrc`, `$HOME/.config/drinkrc` or `$HOME/.drinkrc`.

Example drinkrc with the minimal settings:

    TARGET=somestring
    DRINKDIR="some/path/to/gitdir"

Values can be put in double quotes. Do not put spaces around the '=' if you
want to use the _drink zsh completion file.

For TARGET you should chose a value that is unique to the environment in which
you want to use a certain set of _pydrink_ objects. That could be your hostname
or workplace name. _Pydrink_ will only link objects that are either in your
configured target or in the special 'global' target.

DRINKDIR must be a path to the directory where your _pydrink_ object repository
is located. This contains all your files and it will be the place where
symlinked objects point to. If it is a relative path, $HOME will be prepended
to it implicitly.

DRINKBASEURL should contain the URL for your base repository. This should have
read and write permissions for your user. It's beyond this document to describe
all possible ways to create and reference another git repository, so here is
just one simple example you could use:

    ssh myserver
    cd git
    mkdir dotfiles
    cd dotfiles
    git init --bare

And then use `ssh://myserver/~/git/dotfiles` as DRINKBASEURL.


Shell Integration
------------------

When importing objects, shell completion is extremely helpful when using drink.
For zsh (https://zsh.org), a completion file is provided in **extras/_drink**.
Just drop that somewhere in your fpath and enjoy. Of course import it into your
drink repository.

For adding drink information to your prompt you can use the $drink_prompt_info
variable. This is made available by putting **extras/drinkrefresh** in your
fpath and add it as a precmd hook:

    add-zsh-hook precmd drinkrefresh

$drink_prompt_info will be usually empty. If there are change drink objects, it
will show the number. If your session is not in sync with the repository it will
show a "!". In that case you can run

     drinkrefresh -r

to re-exec zsh.

Use a custom **starship** (https://starship.rs) variable to integrate the
prompt into your starship configuration:

    format = """... $env_var ..."""
    [env_var.drink_prompt_info]
    format = '[$env_value]($style)'
    default = ''
    style = "green"


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

Bootstrap development environment:

    <distro-specific-tool> install pipx
    pipx install poetry
    git clone https://github.com/sstark/pydrink
    cd pydrink
    poetry shell
    poetry update
    make


History
-------

This is yet another dotfile management system. I wrote this originally in zsh
(first commit Mar 14 2008) and use it daily since then.

The zsh version was never published because it is too much entangeled with my
actual shell environment. This rewrite in Python aims to fix that.

Configuration keywords (e. g. "TARGET") are still in upper case to be
compatible with the old shell version of drink. This might change in the future
for a more modern look, but has low priority.


Author
------

Sebastian Stark
