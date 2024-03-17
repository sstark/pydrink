import inspect
from pathlib import Path
from rich import print

DEBUG = False

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
