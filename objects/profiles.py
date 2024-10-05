import os
import yaml
import sys
from utils.colorc import cc


def null_check(value, name, parent):
    if value is None:
        raise ValueError(f"`{name}` for {parent} could not be empty.")


class DeploymentProfile:
    def __init__(self, **kwargs) -> None:
        self.from_dict(kwargs)

    def from_dict(self, d: dict) -> None:
        if isinstance(d, dict):
            if "kubecontexts" in d.keys() and isinstance(d.get("kubecontexts"), list):
                self.kubecontexts = [
                    KubernetesContextProfile(**e) for e in d.get("kubecontexts")
                ]
            else:
                self.kubecontexts = []
            if "docker" in d.keys() and isinstance(d.get("docker"), list):
                self.docker = [DockerImageProfile(**e) for e in d.get("docker")]
            else:
                self.docker = []
            if "helm" in d.keys() and isinstance(d.get("helm"), list):
                self.helm = [HelmPackageProfile(**e) for e in d.get("helm")]
            else:
                self.helm = []
            if "helm_repos" in d.keys() and isinstance(d.get("helm_repos"), list):
                self.repos = [HelmRepoProfile(**e) for e in d.get("helm_repos")]


class KubernetesContextProfile:
    def __init__(self, **kwargs) -> None:
        self.from_dict(kwargs)

    def from_dict(self, d: dict) -> None:
        if isinstance(d, dict):
            self.name = d.get("name")
            self.provider = d.get("provider")
            # provider = azure
            self.subscription = d.get("subscription")
            self.resource_group = d.get("resource_group")
            self.aks_name = d.get("aks_name")


class HelmRepoProfile:
    def __init__(self, **kwargs) -> None:
        self.from_dict(kwargs)

    def from_dict(self, d: dict) -> None:
        if isinstance(d, dict):
            self.name = d.get("name")
            self.url = d.get("url")


class DockerImageProfile:
    def __init__(self, **kwargs) -> None:
        self.from_dict(kwargs)

    def from_dict(self, d: dict) -> None:
        if isinstance(d, dict):
            self.name = d.get("name")
            self.image_name = d.get("image_name")
            self.repository = d.get("repository")
            self.dockerfile = d.get("dockerfile")
            self.context = d.get("context")


class HelmPackageProfile:
    def __init__(self, **kwargs) -> None:
        self.from_dict(kwargs)

    def from_dict(self, d: dict) -> None:
        self.name = d.get("name")
        self.namespace = d.get("namespace")
        self.dpname = d.get("dpname")
        self.package = d.get("package")
        self.repo = d.get("repo")
        self.static_tag = d.get("static_tag")
        self.tag_path = d.get("tag_path")
        if "environments" in d.keys() and isinstance(d.get("environments"), list):
            self.environments = [
                HelmEnvironmentProfile(**e) for e in d.get("environments")
            ]
        else:
            self.environments = []
        assert isinstance(self.environments, list)


class HelmEnvironmentProfile:
    def __init__(self, **kwargs) -> None:
        self.from_dict(kwargs)

    def from_dict(self, d: dict) -> None:
        self.name = d.get("name")
        self.values_file = d.get("values_file")
        self.kubecontext = d.get("kubecontext")


def load_profile(file: str):
    if os.path.exists(file) and os.path.isfile(file):
        with open(file, "r", encoding="utf-8") as f:
            d = yaml.load(f, Loader=yaml.FullLoader)
            return DeploymentProfile(**d)
    else:
        cc.error(f"{file} is not a file or not exists.")
        sys.exit(999)
