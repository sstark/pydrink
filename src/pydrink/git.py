from pydrink.log import debug, err
from pydrink.config import Config
import sys
from typing import Callable
from subprocess import CalledProcessError, call, run
from rich import print


def unclean(c: Config) -> bool:
    ret = call(["git", "-C", str(c['DRINKDIR']), "diff", "--quiet"])
    if ret != 0:
        err(f"drink repository is dirty")
    return ret != 0


def get_branches(c: Config) -> list[str]:
    '''Return a list of all remote branches found in drink repository'''
    try:
        result = run(
            ["git", "-C",
             str(c['DRINKDIR']), "branch", "-r", "--no-color"],
            text=True,
            capture_output=True)
        result.check_returncode()
        if result.stderr:
            err(f"{result.returncode}\n{result.stderr}")
            return []
        if result.stdout:
            return [x.strip() for x in result.stdout.split("\n") if x]
    except CalledProcessError as e:
        err(e.returncode)
    return []


def get_changed_files(c: Config) -> list[str]:
    '''Return a list of all objects with uncommitted changes'''
    try:
        result = run(
            ["git", "-C",
             str(c['DRINKDIR']), "diff-files", "--name-only", "--no-color"],
            text=True,
            capture_output=True)
        result.check_returncode()
        if result.stderr:
            err(f"{result.returncode}\n{result.stderr}")
            return []
        if result.stdout:
            return [x.strip() for x in result.stdout.split("\n") if x]
    except CalledProcessError as e:
        err(e.returncode)
    return []


def menu(c: Config, input_function: Callable) -> int:
    '''Interactive menu to run git commands on drink objects'''
    git = ["git", "-C", str(c["DRINKDIR"])]
    git_cmd = {
        "2": git + ["fetch", str(c["DRINKBASE"])],
        "3": git + ["push", str(c["DRINKBASE"])],
        "5": git + ["commit", "-a"],
        "6": git + ["commit"],
        "7": git + ["log", "-p"],
        "8": git + ["diff"],
    }
    while True:
        print()
        print(" 1) quit")
        print(" 2) fetch from base")
        print(" 3) push to base")
        print(" 4) automerge all remote branches")
        print(" 5) commit -a")
        print(" 6) commit")
        print(" 7) log -p")
        print(" 8) diff")
        print()
        try:
            reply = input_function("[dim]git action[/dim]")
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
