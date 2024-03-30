import inspect
from pathlib import Path
from rich import print

DEBUG = False
QUIET = False
VERBOSE = False


def notice(s):
    """Print normal info messages"""
    # verbose should override quiet
    if (not QUIET) or VERBOSE:
        print(s)


def verbose(s):
    """Print additional info that is not strictly necessary"""
    if VERBOSE:
        print(s)


def warn(s):
    print(s)


def debug(s):
    if not DEBUG:
        return
    caller_frame_record = inspect.stack()[1]
    frame = caller_frame_record[0]
    info = inspect.getframeinfo(frame)
    file = Path(info.filename).name
    print(f"{file}:{info.lineno} {info.function}(): {s}")


def err(s):
    print(f"Error: {s}")
