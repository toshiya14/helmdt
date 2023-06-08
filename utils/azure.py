import subprocess
import sys
import functools
from .colorc import cc as colorc
from .depcheck import checkdep
from .run import run


def login_az():
    checkdep(["az"])
    return run("az login").returncode == 0


def retry_with_login_az(func):
    @functools.wraps(func)
    def wrapper(*argv, **kwargs):
        if not func(*argv, **kwargs):
            colorc.warn(f"Failed to calling {func.__name__} for the first time.")
            if not login_az():
                if not func(*argv, **kwargs):
                    colorc.error("Operation failed even after re-loggin.")
                    sys.exit(-3)
        return True

    return wrapper


@retry_with_login_az
def login_acr(acr_name: str):
    checkdep(["az"])
    return run('az acr login -n "' + acr_name + '"').returncode == 0


def retry_with_login_az_acr(name: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*argv, **kwargs):
            if not func(*argv, **kwargs):
                colorc.warn(f"Failed to calling {func.__name__} for the first time.")
                if not login_acr(name):
                    if not func(*argv, **kwargs):
                        colorc.error("Operation failed even after re-loggin.")
                        sys.exit(-3)
            return True

        return wrapper

    return decorator


@retry_with_login_az
def link_aks(subscription: str, resource_group: str, aks: str):
    checkdep(["az", "kubectl"])
    proc = run(f"az account set --subscription {subscription}")
    if proc.returncode != 0:
        return proc.returncode
    proc = run(f"az aks get-credentials --resource-group {resource_group} --name {aks}")
    return proc.returncode == 0
