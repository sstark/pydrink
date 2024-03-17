from pathlib import Path
import os
import argparse
from collections import defaultdict

from pydrink.config import Config, KINDS
import pydrink.log
from pydrink.log import warn, err, debug
from pydrink.obj import GLOBAL_TARGET

CONFIG_FILENAME = "drinkrc"
DOT_PREFIX = "dot"


class NoConfigFound(Exception):
    '''Raised when no valid configuration could be found'''
    pass


def tracking_status(c: Config, kind: str, p: Path) -> int:
    debug(f"target: {c['TARGET']}, kind: {kind}, file: {p}")
    return 0


def show_untracked_files(c: Config, selected_kind: str = ""):
    '''Show untracked files / possible drink candidates'''
    pat = defaultdict(lambda: "*")
    pat["conf"] = ".*"

    for kind, varname in KINDS.items():
        targetdir = c[varname]
        # Skip the others, if user has selected only a certain kind
        if selected_kind and selected_kind != kind:
            warn(f"skipping {kind}")
            continue
        for f in Path(targetdir).glob(pat[kind]):
            rel_path = f.relative_to(targetdir)
            # TODO: run ignore code here
            if rel_path == targetdir:
                warn(
                    f"Object {rel_path} has the same name as kind {kind}, skipping"
                )
                continue
            # TODO: Return something instead of printing directly
            tracking_status(c, kind, rel_path)


def find_drinkrc() -> Path:
    '''Find a drink configuration file and return its path'''
    if xdgch := os.getenv("XDG_CONFIG_HOME"):
        if (xdgch_p := Path(xdgch) / CONFIG_FILENAME).exists():
            return xdgch_p
    if (xdgdef_p := Path.home() / ".config" / CONFIG_FILENAME).exists():
        return xdgdef_p
    if (drinkrc := Path.home() / ("." + CONFIG_FILENAME)).exists():
        return drinkrc
    raise NoConfigFound("No drinkrc could be found")


def createArgumentParser():
    parser = argparse.ArgumentParser(
        prog='pydrink',
        description='--- DRaft symlINKs in your home ---',
        epilog='Please consult the README for more information.')
    args_main = parser.add_mutually_exclusive_group(required=True)
    args_main.add_argument('-i',
                           '--import',
                           action="store_true",
                           help="import an object")
    args_main.add_argument('-l',
                           '--link',
                           action="store_true",
                           help="add missing symlinks")
    args_main.add_argument('-s',
                           '--show',
                           action="store_true",
                           help="show untracked files")
    args_main.add_argument('-c',
                           '--changed',
                           action="store_true",
                           help="show objects with changes")
    args_main.add_argument('-g',
                           '--git',
                           action="store_true",
                           help="interactive git menu")
    args_main.add_argument('-u',
                           '--dump',
                           action="store_true",
                           help="dump config")
    args_selector = parser.add_argument_group("selectors")
    args_selector.add_argument('-k', '--kind', help=f"one of {set(KINDS)}")
    args_selector.add_argument(
        '-t', '--target', help=f"one of your targets or '{GLOBAL_TARGET}'")
    args_flags = parser.add_argument_group("flags")
    args_flags.add_argument('-v',
                            '--verbose',
                            action="store_true",
                            help="be louder")
    args_flags.add_argument('-q',
                            '--quiet',
                            action="store_true",
                            help="be quieter")
    args_flags.add_argument('-d',
                            '--debug',
                            action="store_true",
                            help="print a lot of debugging information")
    parser.add_argument('filename', nargs="?")
    return parser


def cli():
    parser = createArgumentParser()
    args = parser.parse_args()
    debug(args)
    pydrink.log.DEBUG = args.debug
    # FIXME: Try to not depend on changing PWD
    os.chdir(Path.home())
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
