import subprocess
import platform
import sys
from typing import Callable

from .colorc import cc


def run(
    cmd: str, preferred_shell: list[str] = None, stderr=None, stdout=None, cwd=None
):
    ps = preferred_shell

    if ps is None:
        system = platform.system()
        if system == "Windows":
            ps = ["powershell.exe", "-c"]
        elif system == "Linux" or system == "Unix" or system == "Darwin":
            ps = ["/bin/bash", "-c"]
        else:
            ps = []

    ps.append(cmd)

    return subprocess.run(ps, stderr=stderr, stdout=stdout, cwd=cwd)


def promised_run(
    cmd: str,
    preferred_shell: list[str] = None,
    stderr=None,
    stdout=None,
    cwd=None,
    fallback=None,
):
    proc = run(cmd, preferred_shell, stderr, stdout, cwd)
    if proc.returncode != 0:
        if isinstance(fallback, Callable):
            fallback()
        cc.error(f"Failed to run `{cmd}`.")
        sys.exit(999)


def run_get_output(cmd: str, preferred_shell: list[str] = None, cwd=None):
    proc = run(cmd, preferred_shell, subprocess.PIPE, subprocess.PIPE, cwd)
    return proc.stdout.decode().strip()
