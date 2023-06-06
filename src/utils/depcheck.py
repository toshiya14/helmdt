from reprint import output
from utils.colorc import bcolors, cc
from utils.run import run
import subprocess
import sys

deps = [
    {
        "name": "docker",
        "checkcmd": "docker --version",
        "url": "https://docs.docker.com/engine/install/",
        "checked": False,
    },
    {
        "name": "az",
        "checkcmd": "az version",
        "url": "https://learn.microsoft.com/en-us/cli/azure/",
        "checked": False,
    },
    {
        "name": "git",
        "checkcmd": "git --version",
        "url": "https://git-scm.com/downloads",
        "checked": False,
    },
    {
        "name": "kubectl",
        "checkcmd": "kubectl --help",
        "url": "https://kubernetes.io/docs/",
        "checked": False,
    },
    {
        "name": "helm",
        "checkcmd": "helm --help",
        "url": "https://helm.sh/docs/intro/install/",
        "checked": False,
    },
]


def checkdep(candidates: list[str] = None):
    if candidates is not None:
        tobechecked = []
        for dep in deps:
            if dep["name"] in candidates and not dep["checked"]:
                tobechecked.append(dep)
    else:
        tobechecked = deps

    failed_count = 0

    if len(tobechecked) > 0:
        cc.verbose(
            f"Performs a dependencies checking: {','.join([e['name'] for e in tobechecked])}"
        )

    with output(output_type="list", initial_len=len(tobechecked)) as output_list:
        run_tag = f"\033[{bcolors.BGYELLOW};{bcolors.BLACK}m WAIT \033[0m "
        ok_tag = f"\033[{bcolors.BGGREEN};{bcolors.BLACK}m  OK  \033[0m "
        fail_tag = f"\033[{bcolors.BGRED};{bcolors.BLACK}m FAIL \033[0m "

        for i, dep in enumerate(tobechecked):
            line = f"{run_tag} Checking \033[{bcolors.BLUE}m{dep['name']}\033[0m"
            output_list[i] = line
            dep["checked"] = True

        for i, dep in enumerate(tobechecked):
            cmd = dep["checkcmd"]
            proc = run(cmd, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            if proc.returncode == 0:
                output_list[
                    i
                ] = f"{ok_tag} \033[{bcolors.BLUE}m{dep['name']}\033[0m checked."
            else:
                output_list[
                    i
                ] = f"{fail_tag} Installment for \033[{bcolors.BLUE}m{dep['name']}\033[0m, please see \033[{bcolors.BLUE}m{dep['url']}\033[0m"
                failed_count += 1

    if failed_count > 0:
        cc.error("Failed to check the dependencies.")
        sys.exit(999)
