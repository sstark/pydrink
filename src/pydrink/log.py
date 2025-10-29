import inspect
from pathlib import Path
from rich import print
from rich import console
from textwrap import dedent

DEBUG = False
QUIET = False
VERBOSE = False

c = console.Console()


def notice(s: str, no_dedent=False):
    """Print normal info messages"""
    # verbose should override quiet
    if (not QUIET) or VERBOSE:
        if no_dedent:
            c.print(s)
        else:
            c.print(dedent(s))


def verbose(s: str):
    """Print additional info that is not strictly necessary"""
    if VERBOSE:
        c.print("[dim]" + dedent(s) + "[/dim]")


def warn(s: str):
    c.print("! [yellow]" + dedent(s) + "[/yellow]")


def debug(s: str):
    if not DEBUG:
        return
    caller_frame_record = inspect.stack()[1]
    frame = caller_frame_record[0]
    info = inspect.getframeinfo(frame)
    file = Path(info.filename).name
    print(f"{file}:{info.lineno} {info.function}(): {s}")


def err(s: str):
    c.print("[bright_red]" + dedent(s) + "[/bright_red]")
