from collections.abc import Iterable, Iterator
from pydrink.log import debug, err, notice, warn
from pydrink.config import Config, KINDS
from pydrink.obj import DrinkObject
import sys
import getpass
from typing import Callable, Dict
from subprocess import CalledProcessError, call, run


def unclean(c: Config) -> bool:
    ret = call(["git", "-C", str(c.drinkdir), "diff", "--quiet"])
    if ret != 0:
        err("drink repository is dirty")
    return ret != 0


def get_branches(c: Config) -> list[str]:
    """Return a list of all remote branches found in drink repository"""
    try:
        result = run(
            ["git", "-C", str(c.drinkdir), "branch", "-r", "--no-color"],
            text=True,
            capture_output=True,
        )
        result.check_returncode()
        if result.stderr:
            err(f"{result.returncode}\n{result.stderr}")
            return []
        if result.stdout:
            return [x.strip() for x in result.stdout.split("\n") if x]
    except CalledProcessError as e:
        err(e.returncode)
    return []


def diff(c: Config) -> int:
    """Print a list of uncommitted changes"""
    return call(["git", "-C", str(c.drinkdir), "diff"])


def get_changed_files(c: Config) -> list[str]:
    """Return a list of all objects with uncommitted changes"""
    try:
        result = run(
            [
                "git",
                "-C",
                str(c.drinkdir),
                "diff-files",
                "--name-only",
                "--no-color",
            ],
            text=True,
            capture_output=True,
        )
        result.check_returncode()
        if result.stderr:
            err(f"{result.returncode}\n{result.stderr}")
            return []
        if result.stdout:
            return [x.strip() for x in result.stdout.split("\n") if x]
    except CalledProcessError as e:
        err(e.returncode)
    return []


def get_tracked_objects(c: Config, kinds: Iterable[str] = []) -> Iterator[DrinkObject]:
    """Return a list of DrinkObjects with all tracked objects"""
    cmd = ["git", "-C", str(c.drinkdir), "ls-files"]
    if kinds == []:
        kinds = list(KINDS)
    try:
        result = run(cmd + list(kinds), text=True, capture_output=True)
        result.check_returncode()
        if result.stderr:
            err(f"{result.returncode}\n{result.stderr}")
        if result.stdout:
            debug("git ls-files worked")
            for line in result.stdout.split("\n"):
                if not line:
                    continue
                debug(f"next line to process: {line}")
                yield DrinkObject(c, c.drinkdir / line.strip())
    except CalledProcessError as e:
        err(f"listing tracked objects: {e}")


def add_object(c: Config, obj: DrinkObject) -> int:
    """Add and commit a drink object to the git repository after it was copied.
    Second step of an import of a new object"""
    cmd = ["git", "-C", str(c.drinkdir), "add", obj.get_repopath(relative=True)]
    ret = call(cmd)
    if ret != 0:
        err(f"Error when adding object to repository. {cmd} failed.")
        return ret
    cmd = ["git", "-C", str(c.drinkdir), "commit"]
    ret = call(cmd)
    if ret != 0:
        err(f"Error when committing to repository. {cmd} failed.")
    return ret


def init_repository(c: Config) -> int:
    notice(f'Initializing git repository in {c.drinkdir}:')
    repo = c.drinkdir
    debug(f"creating directory {repo}")
    repo.mkdir(parents=True)
    base = c["DRINKBASE"]
    baseurl = c["DRINKBASEURL"]
    mb = c["MASTERBRANCH"]
    cf_email = target = c["TARGET"]
    cf_username = getpass.getuser()
    cf_push = f"+refs/heads/*:refs/remotes/{target}/*"
    cf_fetch = f"+refs/remotes/*/{mb}:refs/remotes/*/{mb}"
    git = ["git", "-C", str(repo)]
    cmd = git + ["init", "-b", mb]
    ret = call(cmd)
    if ret != 0:
        err(f"Could not initialize repository: {cmd}")
        return ret
    notice("A drink repository has been created.")
    if baseurl:
        notice("Configuring git remote.")
        cmd = git + ["remote", "add", base, baseurl]
        if (ret := call(cmd)) != 0:
            err(f"Could not add remote: {cmd}")
            return ret
        cmd = git + ["config", f"remote.{base}.push", cf_push]
        if (ret := call(cmd)) != 0:
            err(f"Could not configure push mode: {cmd}")
            return ret
        cmd = git + ["config", f"remote.{base}.fetch", cf_fetch]
        if (ret := call(cmd)) != 0:
            err(f"Could not configure fetch mode: {cmd}")
            return ret
        cmd = git + ["config", "user.name", cf_username]
        if (ret := call(cmd)) != 0:
            warn(f"Could not configure username: {cmd}")
        cmd = git + ["config", "user.email", cf_email]
        if (ret := call(cmd)) != 0:
            warn(f"Could not configure email: {cmd}")
        notice("""\
            Now you should be able to automerge from all remotes:

              drink -g <<<4

            And add all (missing) symlinks:

              drink -lv
            """)
    else:
        warn("No DRINKBASEURL is defined, remote features will be unavailable.")
    return 0


def git_menu_items(c: Config, git: list[str]) -> dict[str, list[str]]:
    """Return a dictionary of user selectable git commands, indexed by a number."""
    git_cmd_base: Dict[str, list[str]] = {
        "2": git + ["fetch", str(c["DRINKBASE"])],
        "3": git + ["push", str(c["DRINKBASE"])],
        "5": git + ["commit", "-a"],
        "6": git + ["commit"],
        "7": git + ["log", "-p"],
        "8": git + ["diff"],
    }
    change_actions = ["diff", "commit", "checkout", "add"]
    notice("")
    notice(" 1) [b]quit[/b]", no_dedent=True)
    notice(" 2) [b]fetch[/b] from base", no_dedent=True)
    notice(" 3) [b]push[/b] to base", no_dedent=True)
    notice(" 4) [b]automerge[/b] all remote branches", no_dedent=True)
    notice(" 5) [b]commit -a[/b]", no_dedent=True)
    notice(" 6) [b]commit[/b]", no_dedent=True)
    notice(" 7) [b]log -p[/b]", no_dedent=True)
    notice(" 8) [b]diff[/b]", no_dedent=True)
    i: int = 10
    # If one of the individual action commands is used,
    # the corresponding menu entries are still there. So
    # we need to reset the whole menu on each loop.
    git_cmd = git_cmd_base
    # Augment the menu with changed objects
    changed_files = get_changed_files(c)
    for change in changed_files:
        notice(f" [yellow]------ ({change}) ------[/yellow]")
        for action in change_actions:
            notice(f"{i:>2}) {action} [dim]{change}[/dim]")
            git_cmd[str(i)] = git + [action] + [change]
            i += 1
    notice("")
    return git_cmd


def menu(c: Config, input_function: Callable) -> int:
    """Interactive menu to run git commands on drink objects"""
    while True:
        # The git base command which is the same for all menu items
        git = ["git", "-C", str(c.drinkdir)]
        # Populate the menu
        git_cmd = git_menu_items(c, git)
        debug(f"git_cmd: {git_cmd}")
        try:
            reply = input_function()
        except EOFError:
            return 0
        debug(f"reply: {reply}")
        if reply == "1":
            return 0
        if reply in git_cmd:
            debug(f"calling: {' '.join(git_cmd[reply])}")
            ret = call(git_cmd[reply])
            # git will be killed with signal 13 (SIGPIPE) when there is a lot
            # of output and 'q' is pressed early (broken pipe). We can ignore
            # that.
            if ret not in [-13, 0]:
                err(f"git returned error {ret}")
            else:
                ret = 0
        elif reply == "4":
            if unclean(c):
                err("Stopping automerge")
                continue
            debug("git fetch from base")
            ret = call(git_cmd["2"])
            if ret != 0:
                err(f"git returned error {ret} when fetching from base")
                err("Stopping automerge")
                continue
            branches = get_branches(c)
            debug(f"found branches: {branches}")
            for branch in branches:
                ret = call(git + ["merge", branch])
                if ret != 0:
                    err(f"error {ret} when trying to merge {branch}")
                    err("Stopping automerge")
                    continue
        else:
            err(f"Invalid menu item selected: {reply}")
            ret = 99
        # Prevent showing the input prompt again when there is no tty.
        # Even in case of no tty we want to ask for input() above to support
        # things like "drink -g <<<7"
        if not sys.stdin.isatty():
            debug("no tty, exit from loop")
            return ret
