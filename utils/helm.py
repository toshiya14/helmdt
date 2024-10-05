import subprocess

from objects.profiles import HelmRepoProfile
from .azure import retry_with_login_az_acr
from .depcheck import checkdep
from .run import run, promised_run, run_get_output


def apply_helm_package(
    dpname: str,
    namespace: str,
    kubecontext: str,
    package: str,
    values: str,
    tag: str,
    repo: HelmRepoProfile | None,
    tag_path: str,
):
    checkdep(["helm", "kubectl"])

    # create namespace if not exists
    current_context = run_get_output("kubectl config current-context")

    def resume_context():
        run(f'kubectl config use-context "{current_context}"')

    promised_run(f'kubectl config use-context "{kubecontext}"', fallback=resume_context)
    proc = run(
        f'kubectl get namespace "{namespace}"',
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )
    if proc.returncode != 0:
        promised_run(f'kubectl create namespace "{namespace}"', fallback=resume_context)

    if repo is not None:
        # use remote chart
        cmd = f'helm install "{dpname}" "{repo.name}/{package}" --kube-context "{kubecontext}" -n "{namespace}" -f "{values}"'
    else:
        # use local chart
        cmd = f'helm upgrade --kube-context "{kubecontext}" --install "{dpname}" "{package}" -n "{namespace}" -f "{values}"'

    if tag is not None and len(tag) > 0:
        cmd = cmd + f' --set {tag_path}="{tag}"'

    promised_run(cmd, fallback=resume_context)
    resume_context()


def add_repo(name: str, url: str):
    checkdep(["helm"])

    run(f'helm repo add "{name}" "{url}"')
    promised_run(f"helm repo update")
