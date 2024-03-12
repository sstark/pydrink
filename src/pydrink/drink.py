#!/usr/bin/env python

from subprocess import run, CalledProcessError

def cli():
    try:
        result = run("echo bla",shell=True, capture_output=True, text=True)
        result.check_returncode()
    except CalledProcessError as e:
        print(f"Error {e.returncode}\n{result.stderr}")
    print(result.stdout)
