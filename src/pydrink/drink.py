
from subprocess import run, CalledProcessError
from pathlib import Path
import os
from collections import defaultdict

from pydrink.config import Config, KINDS
from pydrink.log import warn, err, debug
from pydrink.obj import DrinkObject

CONFIG_FILENAME = ".drinkrc"
DOT_PREFIX = "dot"

def tracking_status(c: Config, kind: str, p: Path) -> int:
    debug(f"target: {c['TARGET']}, kind: {kind}, file: {p}")
    return 0

def show_untracked_files(c: Config, selected_kind: str=None):
    '''Show untracked files / possible drink candidates'''
    # 1. Differenziere, welches $kind global über die cli angegeben wurde
    #   a. alle kinds
    #   b. nur ein kind
    # 2. Iteriere über alle angegebenen kinds
    #   1. Finde targetdir für kind (get_kinddir())
    #       -> Exception wenn nicht vorhanden
    #   2. Fallunterscheidung:
    #       a. kind=conf: kindfiles = $targetdir/.*
    #       b. ansonsten: kindfiles = $targetdir/*
    #   3. Iteriere über alle kindfiles:
    #       0. Schneide Pfad ab, also /home/bla/bin/foo -> foo
    #       1. Wenn in "ignore", skippen
    #       2. Wenn der filename einem key aus KINDDIR entspricht, skippen
    #       3. is_tracked(file, kind)
    #       Jetzt je nach tracking status ausgeben

    pat = defaultdict(lambda:"*")
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
                warn(f"Object {rel_path} has the same name as kind {kind}, skipping")
                continue
            # TODO: Return something instead of printing directly
            tracking_status(c, kind, rel_path)


def cli():
    # FIXME: Try to not depend on changing PWD
    os.chdir(Path.home())
    try:
        result = run("echo bla",shell=True, capture_output=True, text=True)
        result.check_returncode()
    except CalledProcessError as e:
        err(f"{e.returncode}\n{result.stderr}")
    # print(result.stdout)
    c = Config(Path.home() / CONFIG_FILENAME)
    debug(c)
    show_untracked_files(c, selected_kind='conf')
    do = DrinkObject('bin', 'singold', 'tiv')
    debug(do)
