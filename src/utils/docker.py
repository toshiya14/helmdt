from utils.azure import login_acr
from utils.depcheck import checkdep
from utils.run import promised_run
from utils.colorc import cc
import sys
import re

re_remote_image = re.compile(r"^(.*?)\.azurecr\.io\/(.*)$")

def build_docker_image(dockerfile: str, build_context: str, image_name: str, no_cache:bool = False):
    checkdep(["docker"])
    cmd = f'docker build -t "{image_name}" -f "{dockerfile}" "{build_context}"'
    if no_cache:
        cmd += " --no-cache"
    promised_run(cmd)
    
def push_docker_image(local_image_name: str, remote_image_path: str, tag: str):
    deps = ["docker"]
    
    match = re_remote_image.match(remote_image_path)
    if match:
        deps.append("az")
        repo_name = match.group(1)
    else:
        cc.error(f"Invalid remote_image_path: {remote_image_path}")
        sys.exit(999)
    
    checkdep(deps)
    
    login_acr(repo_name)
    
    promised_run(f'docker tag "{local_image_name}" "{remote_image_path}:{tag}"')
    promised_run(f'docker push "{remote_image_path}:{tag}"')
