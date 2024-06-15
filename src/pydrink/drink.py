from collections.abc import Iterator
from enum import Enum
from pathlib import Path
import os
import argparse
from collections import defaultdict
from importlib.metadata import metadata, version
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich import print
from rich_argparse import RichHelpFormatter

from pydrink.config import BY_TARGET, Config, KINDS, CONFIG_FILENAME
import pydrink.log
from pydrink.log import err, debug, verbose, warn, notice
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
    if (link_target := p.readlink()).is_relative_to(c.drinkdir):
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
    if not dir.exists():
        return
    debug(f"pruning {dir}")
    for p in dir.iterdir():
        if not p.is_symlink():
            debug(f"{p} is not a symlink")
            continue
        dest = p.readlink()
        debug(f"{p} points to {dest}")
        if not dest.is_relative_to(c.drinkdir / selected_kind):
            continue
        if dest.exists():
            continue
        debug(f"{p} is dangling")
        yield p


def prune(c: Config) -> int:
    """Remove all dangling symlinks from $HOME that are likely to
    be leftovers from removed drink objects"""
    verbose("pruning...")
    for kind in KINDS:
        for dl in get_dangling_links(c, kind):
            verbose(f"dangling symlink {dl}")
            try:
                dl.unlink()
            except OSError as e:
                err(f"Could not remove dangling symlink {dl}: {e}")
                return 4
    return 0


def link_all(c: Config) -> int:
    verbose("linking...")
    for o in git.get_tracked_objects(c):
        if o.state == ObjectState.ManagedPending:
            verbose(f"linking {o.relpath}")
            try:
                o.link()
            except OSError as e:
                err(f"could not link {o.relpath}: {e}")
                return 4
    return 0


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
    if not (c.drinkdir / ".git").is_dir():
        warn(f"""\
            Configuration found in {drinkrc}, but the configured git repository does
            not exist yet.""")
        git.init_repository(c)
    else:
        warn(f"""\
            Configuration found in {drinkrc}. Remove it first if you want to start
            over.""")
    return 0


def createArgumentParser():
    parser = argparse.ArgumentParser(
        prog="drink",
        description="Distributed Reusage of Invaluable Nerd Kit",
        epilog="Please consult the README for more information.",
        formatter_class=RichHelpFormatter,
    )
    args_main = parser.add_mutually_exclusive_group(required=True)
    args_main.add_argument(
        "-r", "--readme", action="store_true", help="show readme"
    )
    args_main.add_argument(
        "-b", "--begin", action="store_true", help="initialize drink"
    )
    args_main.add_argument(
        "-i", "--import", dest="imp", action="store_true", help="import an object"
    )
    args_main.add_argument(
        "-l", "--link", action="store_true", help="add missing and prune symlinks"
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
    args_main.add_argument(
        "-V", "--version", action="store_true", help="show version"
    )
    args_main.add_argument("-u", "--dump", nargs="?", const="_ALL", action="store",
                           help="dump config. With argument, dump only that single \
                           variable's expanded value")
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


def handleArgs(c: Config, args: argparse.Namespace) -> int:
    p_name = __package__ or __name__
    debug(f"p_name: {p_name}")
    if args.dump:
        debug(args.dump)
        if args.dump == "_ALL":
            print(c)
        else:
            try:
                print(c[args.dump])
            except KeyError:
                err(f"No such variable: {args.dump}")
                return 6
        return 0
    if args.show:
        try:
            show_untracked_files(c, selected_kind=args.kind)
            return 0
        except Exception as e:
            err(e)
            return 1
    if args.git:
        prompt = Prompt("" if args.quiet else "[dim][i]git action[/i][/dim]: ")
        prompt.prompt_suffix = ""
        try:
            return git.menu(c, prompt)
        except KeyboardInterrupt:
            err("git menu was cancelled")
            return 1
    if args.changed:
        if args.verbose:
            return git.diff(c)
        else:
            print("\n".join(git.get_changed_files(c)))
            return 0
    if args.link:
        if (ret := link_all(c)) != 0:
            return ret
        if (ret := prune(c)) != 0:
            return ret
        return 0
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
            return 0
        except OSError as e:
            err(f"Import failed: {e}")
            return 2
        except InvalidKind:
            err(f"Import failed: {args.kind} is not a valid kind")
            return 2
        except InvalidDrinkObject as e:
            err(f"Import failed: {e}")
            return 2
    if args.readme:
        if descr := metadata(p_name).get("Description"):
            print(Markdown(descr))
            return 0
        else:
            err("You need Python >= 3.10 to use this feature.")
            return 5
    if args.readme:
        meta = metadata(p_name)
        print(Markdown(meta["Description"]))
        return 0
    if args.version:
        p_version = version(p_name)
        notice(f"{p_name} {p_version}")
        return 0
    err(f"Invalid arguments: {args}")
    return 9


def cli() -> int:
    parser = createArgumentParser()
    args = parser.parse_args()
    debug(args)
    pydrink.log.DEBUG = args.debug
    pydrink.log.QUIET = args.quiet
    pydrink.log.VERBOSE = args.verbose

    # We probably have no config yet if this is called,
    # so handleArgs() would be too late.
    if args.begin:
        return begin_setup()

    try:
        c = Config(find_drinkrc())
    except Exception as e:
        err(e)
        return 1
    debug(c)

    return handleArgs(c, args)
