from typing import Union
import click
import yaml
import os
import sys
from InquirerPy import prompt, inquirer
from pathlib import Path

from objects.profiles import (
    HelmEnvironmentProfile,
    HelmPackageProfile,
    load_profile,
    DeploymentProfile,
)
from utils.run import run, run_get_output
from utils.azure import link_aks
from utils.colorc import cc
from utils.depcheck import checkdep
from utils.docker import build_docker_image, push_docker_image
from utils.helm import apply_helm_package


class runtime:
    def __init__(
        self,
        profile_file: str = None,
        profile: DeploymentProfile = None,
        values: dict = {},
    ) -> None:
        self.profile = profile
        self.profile_file = profile_file
        self.values = values


RUNTIME: runtime = runtime()


def __pick_using_profile(
    cols: dict,
    yes: bool,
    key: Union[str, None],
    key_option: str,
    question: str,
    section: str,
):
    if key is None and len(cols.values()) > 1:
        if yes:
            cc.error(f"--yes sepacified, but {key_option} not specified.")
            sys.exit(-3)
        result = inquirer.select(question, cols.keys()).execute()

        selected_profile = cols[result]
    elif len(cols.values()) == 1:
        selected_profile = list(cols.values())[0]
    else:
        selected_profile = cols.get(key)
        if selected_profile is None:
            cc.error(f"`{key}` profile is not defined in `{section}` section.")
            sys.exit(999)

    return selected_profile


@click.group()
@click.option(
    "--profile",
    "-f",
    type=click.Path(),
    help="The deployment profile path.",
    default=os.path.join(os.getcwd(), "helmdt.yaml"),
)
def main(profile: str):
    cc.verbose(f"Use profile: {profile}")
    RUNTIME.profile_file = profile
    RUNTIME.profile = load_profile(profile)

    # replace placeholders
    parent_path_for_profile = Path(os.path.realpath(profile)).parent.absolute()
    gitroot_for_ppp = run_get_output(
        "git rev-parse --show-toplevel", cwd=parent_path_for_profile
    )
    githash_for_ppp = run_get_output(
        "git rev-parse --short HEAD", cwd=parent_path_for_profile
    )

    def rep_str(s: str):
        return s.replace("$(gitroot)", gitroot_for_ppp).replace(
            "$(githash)", githash_for_ppp
        )

    RUNTIME.values["githash"] = githash_for_ppp
    RUNTIME.values["gitroot"] = gitroot_for_ppp
    RUNTIME.values["image_tag"] = f"build-{RUNTIME.values['githash']}"

    for docker in RUNTIME.profile.docker:
        docker.dockerfile = rep_str(docker.dockerfile)
        docker.context = rep_str(docker.context)

    for helm in RUNTIME.profile.helm:
        helm.package = rep_str(helm.package)
        for env in helm.environments:
            env.values_file = rep_str(env.values_file)


@main.command()
@click.option(
    "-n", "--name", type=click.STRING, help="The name for the docker image to build."
)
@click.option(
    "--no-cache", is_flag=True, help="Disable cache while build the docker image."
)
@click.option(
    "--yes",
    is_flag=True,
    help="Disable any prompt, this option need the essential field to be specified from the command line options.",
)
def build(name: str, no_cache: bool, yes: bool):
    docker_profiles = {e.name: e for e in RUNTIME.profile.docker}
    using_docker_profile = __pick_using_profile(
        docker_profiles,
        yes,
        name,
        "-n/--name",
        "Select a docker profile to build:",
        "docker",
    )

    # confirm build information
    if not yes:
        print("==================")
        cc.label("Dockerfile", using_docker_profile.dockerfile)
        cc.label("Build Context", using_docker_profile.context)
        cc.label("Image Name", using_docker_profile.image_name)
        print("-------------------")
        result = inquirer.confirm("Confirm to build", default=True).execute()
        if not result:
            cc.warn("User aborted.")
            sys.exit(999)

    # build
    build_docker_image(
        dockerfile=using_docker_profile.dockerfile,
        build_context=using_docker_profile.context,
        image_name=using_docker_profile.image_name,
        no_cache=no_cache,
    )

    # ask push
    image_full_path = (
        f"{using_docker_profile.repository}/{using_docker_profile.image_name}"
    )
    print("==================")
    cc.label("Local Image Name", using_docker_profile.image_name)
    cc.label("Remote Image Name", image_full_path)
    cc.label("Image Tag", RUNTIME.values["image_tag"])
    print("-------------------")

    if not yes:
        result = inquirer.confirm(
            "Are you also want to push to remote repository?", default=True
        ).execute()

        if not result:
            cc.warn("User aborted")
            sys.exit(999)

    # TODO: Check if tag already exists.

    # push
    push_docker_image(
        local_image_name=using_docker_profile.image_name,
        remote_image_path=image_full_path,
        tag=RUNTIME.values["image_tag"],
    )


@main.command()
@click.option("-n", "--name", type=click.STRING, help="The name of helm profile.")
@click.option("-e", "--env", type=click.STRING, help="The env name.")
@click.option(
    "--yes",
    is_flag=True,
    help="Disable any prompt, this option need the essential field to be specified from the command line options.",
)
def apply(name: str = None, env: str = None, yes: bool = False):
    helm_profiles = {e.name: e for e in RUNTIME.profile.helm}
    using_helm_profile: HelmPackageProfile = __pick_using_profile(
        helm_profiles,
        yes,
        name,
        "-n/--name",
        "Select a helm package profile to apply:",
        "helm",
    )

    # ask env
    envs = {e.name: e for e in using_helm_profile.environments}
    using_env: HelmEnvironmentProfile = __pick_using_profile(
        envs,
        yes,
        env,
        "-e/--env",
        "Select an environment to apply:",
        f"helm[name={using_helm_profile.name}].environments",
    )

    # confirm apply
    if not yes:
        print("==================")
        cc.label("Deployment Name", using_helm_profile.dpname)
        cc.label("Docker Image Tag", RUNTIME.values["image_tag"])
        cc.label("Kubernetes Context", using_env.kubecontext)
        cc.label("Namespace", using_helm_profile.namespace)
        cc.label("Package Path", using_helm_profile.package)
        cc.label("Values File", using_env.values_file)
        print("-------------------")
        result = inquirer.confirm("Confirm to apply", default=True).execute()
        if not result:
            cc.warn("User aborted.")
            sys.exit(999)

    apply_helm_package(
        dpname=using_helm_profile.dpname,
        namespace=using_helm_profile.namespace,
        kubecontext=using_env.kubecontext,
        package=using_helm_profile.package,
        values=using_env.values_file,
        tag=RUNTIME.values["image_tag"],
    )


@main.command()
def depcheck():
    checkdep()


@main.command()
@click.option(
    "-n", "--name", type=click.STRING, help="The name of kubernetes context profile."
)
def link(name: str = None):
    kubernetes_services = {e.name: e for e in RUNTIME.profile.kubecontexts}

    if name is None:
        result = inquirer.checkbox(
            "Which service do you want to link: (Space to select, Enter to confirm)",
            [e.name for e in kubernetes_services.values()],
        ).execute()
    else:
        result = [name]

    for service_name in result:
        if service_name not in kubernetes_services.keys():
            cc.error(f"{service_name} is not defined in `kubecontexts` section.")
            sys.exit(999)
        service = kubernetes_services[service_name]
        if service.provider == "azure":
            link_aks(service.subscription, service.resource_group, service.aks_name)
