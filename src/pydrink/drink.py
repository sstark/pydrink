from collections.abc import Iterator
from enum import Enum
from pathlib import Path
import os
import argparse
from collections import defaultdict
from rich.prompt import Prompt
from rich_argparse import RichHelpFormatter

from pydrink.config import BY_TARGET, Config, KINDS, CONFIG_FILENAME
import pydrink.log
from pydrink.log import err, debug, verbose, warn
from pydrink.obj import (
    GLOBAL_TARGET,
    DrinkObject,
    InvalidDrinkObject,
    InvalidKind,
    ObjectState,
)
import pydrink.git as git


class TrackingState(Enum):
    Unknown = 1
    Untracked = 2
    TrackedGlobal = 3
    TrackedHere = 4
    TrackedOther = 5


class NoConfigFound(Exception):
    """Raised when no valid configuration could be found"""

    pass


def tracking_status(c: Config, p: Path) -> TrackingState:
    if not p.is_symlink():
        return TrackingState.Untracked
    if (link_target := p.readlink()).is_relative_to(c["DRINKDIR"]):
        if BY_TARGET in link_target.parts:
            return TrackingState.TrackedHere
        else:
            return TrackingState.TrackedGlobal
    return TrackingState.Unknown


def show_untracked_files(c: Config, selected_kind: str = ""):
    """Show untracked files / possible drink candidates"""
    pat = defaultdict(lambda: "*")
    pat["conf"] = ".*"

    for kind, varname in KINDS.items():
        checkdir = Path.home() / c[varname]
        # Skip the others, if user has selected only a certain kind
        if selected_kind and selected_kind != kind:
            debug(f"skipping {kind}")
            continue
        for f in checkdir.glob(pat[kind]):
            ts = tracking_status(c, f)
            if ts == TrackingState.Untracked:
                print(f"{f}")


def get_dangling_links(c: Config, selected_kind: str) -> Iterator[Path]:
    """Return an Iterator of Paths, if those paths are:
    1. absolute
    2. are in a valid kindDir
    3. resolve to a non-existing Path in DRINKDIR
    """
    dir = c.kindDir(selected_kind)
    verbose(f"pruning {dir}")
    for p in dir.iterdir():
        if not p.is_symlink():
            debug(f"{p} is not a symlink")
            continue
        dest = p.readlink()
        debug(f"{p} points to {dest}")
        if not dest.is_relative_to(c["DRINKDIR"] / selected_kind):
            continue
        if dest.exists():
            continue
        debug(f"{p} is dangling")
        yield p


def find_drinkrc() -> Path:
    """Find a drink configuration file and return its path"""
    if xdgch := os.getenv("XDG_CONFIG_HOME"):
        if (xdgch_p := Path(xdgch) / CONFIG_FILENAME).exists():
            return xdgch_p
    if (xdgdef_p := Path.home() / ".config" / CONFIG_FILENAME).exists():
        return xdgdef_p
    if (drinkrc := Path.home() / ("." + CONFIG_FILENAME)).exists():
        return drinkrc
    raise NoConfigFound("No drinkrc could be found")


def begin_setup() -> int:
    try:
        drinkrc = find_drinkrc()
        c = Config(drinkrc)
    except NoConfigFound:
        return Config.create_drinkrc()
    except Exception as e:
        err(f"Unexpected error: {e}")
        return 3
    if not (c["DRINKDIR"] / ".git").is_dir():
        warn(
            f"Configuration found in {drinkrc}, but the configured git repository does not exist yet."
        )
        git.init_repository(c)
    else:
        warn(
            f"Configuration found in {drinkrc}. Remove it first if you want to start over."
        )
    return 0


def createArgumentParser():
    parser = argparse.ArgumentParser(
        prog="pydrink",
        description="Distributed Reusage of Invaluable Nerd Kit",
        epilog="Please consult the README for more information.",
        formatter_class=RichHelpFormatter,
    )
    args_main = parser.add_mutually_exclusive_group(required=True)
    args_main.add_argument(
        "-b", "--begin", action="store_true", help="initialize drink"
    )
    args_main.add_argument(
        "-i", "--import", dest="imp", action="store_true", help="import an object"
    )
    args_main.add_argument(
        "-l", "--link", action="store_true", help="add missing symlinks"
    )
    args_main.add_argument(
        "-s", "--show", action="store_true", help="show untracked files"
    )
    args_main.add_argument(
        "-c", "--changed", action="store_true", help="show objects with changes"
    )
    args_main.add_argument(
        "-g", "--git", action="store_true", help="interactive git menu"
    )
    args_main.add_argument("-u", "--dump", action="store_true", help="dump config")
    args_selector = parser.add_argument_group("selectors")
    args_selector.add_argument("-k", "--kind", help=f"one of {set(KINDS)}")
    args_selector.add_argument(
        "-t", "--target", help=f"one of your targets or '{GLOBAL_TARGET}'"
    )
    args_flags = parser.add_argument_group("flags")
    args_flags.add_argument("-v", "--verbose", action="store_true", help="be louder")
    args_flags.add_argument("-q", "--quiet", action="store_true", help="be quieter")
    args_flags.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="print a lot of debugging information",
    )
    parser.add_argument("filename", nargs="?")
    return parser


def cli():
    parser = createArgumentParser()
    args = parser.parse_args()
    debug(args)
    pydrink.log.DEBUG = args.debug
    pydrink.log.QUIET = args.quiet
    pydrink.log.VERBOSE = args.verbose

    if args.begin:
        return begin_setup()

    try:
        c = Config(find_drinkrc())
    except Exception as e:
        err(e)
        return 1
    debug(c)
    if args.dump:
        print(c)
        return 0
    if args.show:
        try:
            show_untracked_files(c, selected_kind=args.kind)
        except Exception as e:
            err(e)
            return 1
    if args.git:
        try:
            return git.menu(c, Prompt.ask)
        except KeyboardInterrupt:
            err("git menu was cancelled")
            return 1
    if args.changed:
        if args.verbose:
            git.diff(c)
        else:
            print("\n".join(git.get_changed_files(c)))
    if args.link:
        for o in git.get_tracked_objects(c):
            if o.state == ObjectState.ManagedPending:
                verbose(f"linking {o.relpath}")
                o.link()
    if args.imp:
        if not args.kind:
            err("no kind supplied")
            return 2
        if not args.target:
            err("no target supplied")
            return 2
        if not args.filename:
            err("no filename supplied")
            return 2
        try:
            o = DrinkObject.import_object(
                c, Path(args.filename), args.kind, args.target
            )
            git.add_object(c, o)
            o.link(overwrite=True)
        except FileNotFoundError as e:
            err(f"Import failed: {e}")
            return 2
        except InvalidKind:
            err(f"Import failed: is not a valid kind")
            return 2
        except InvalidDrinkObject as e:
            err(f"Import failed: {e}")
            return 2
