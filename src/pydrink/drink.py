#!/usr/bin/env python

from subprocess import run, CalledProcessError
from pathlib import Path
import os

KINDS = {
    "bin":      "bin",
    "zfunc":    ".zfunc",
    "conf":     "."
}

def warn(s):
    # TODO: Implement logging
    print(s)

def tracking_status(kind: str, p: Path) -> int:
    # TODO: get DRINKDIR
    # FIXME: TARGET is global in original
    print(kind, p)
    pass

def show_untracked_files(selected_kind: str=None):
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

    for kind, targetdir in KINDS.items():
        # Skip the others, if user has selected only a certain kind
        if selected_kind and selected_kind != kind:
            warn(f"skipping {kind}")
            continue
        if kind == "conf":
            pat = ".*"
        else:
            pat = "*"
        for f in Path(targetdir).glob(pat):
            rel_path = f.relative_to(targetdir)
            # TODO: run ignore code here
            if rel_path == targetdir:
                warn(f"Object {rel_path} has the same name as kind {kind}, skipping")
                continue
            # TODO: Return something instead of printing directly
            print(tracking_status(rel_path))


def cli():
    # FIXME: Try to not depend on changing PWD
    os.chdir(Path.home())
    try:
        result = run("echo bla",shell=True, capture_output=True, text=True)
        result.check_returncode()
    except CalledProcessError as e:
        print(f"Error {e.returncode}\n{result.stderr}")
    # print(result.stdout)
    show_untracked_files()
