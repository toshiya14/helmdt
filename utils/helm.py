import subprocess
from .azure import retry_with_login_az_acr
from .depcheck import checkdep
from .run import run, promised_run, run_get_output


def apply_helm_package(
    dpname: str, namespace: str, kubecontext: str, package: str, values: str, tag: str
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

    cmd = f'helm upgrade --kube-context "{kubecontext}" --install "{dpname}" "{package}" -n "{namespace}" -f "{values}" --set image.tag="{tag}"'

    promised_run(cmd, fallback=resume_context)
    resume_context()
