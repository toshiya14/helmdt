# HELM Deployment Toolkit

A deployment toolkit that support:

- Build and push docker image. (Now supported container repositories: `AzureCR`)
- Apply helm packages and values.
- Link to aks. (Azure kubenetes services)

And you could use it with both command-line and guiding ways.

* [Installation](#installation)
  * [via pip](#via-pip)
  * [via release](#via-release)
* [Guiding Way](#guiding-way)
  * [Manually specify the profile](#manually-specify-the-profile)
    * [-f | File](#-f--file)
  * [Actions](#actions)
    * [depcheck](#depcheck)
    * [build](#build)
    * [apply](#apply)
    * [link](#link)
* [Command Line Way](#command-line-way)
  * [--yes | Yes](#--yes--yes)
  * [-n/--name | Name](#-n--name--name)
  * [-e/--env | Environment](#-e--env--environment)
  * [--no-cache | Stop using cache](#--no-cache--stop-using-cache)
* [Profile file structure](#profile-file-structure)
  * [\<root\>](#root)
  * [Kubernetes Context Profile](#kubernetes-context-profile)
  * [Docker Image Profile](#docker-image-profile)
  * [HELM Package Profile](#helm-package-profile)
  * [Helm Environment Profile](#helm-environment-profile)
  * [Variables](#variables)
  * [Example](#example)

## Installation

### via pip

```bash
pip install helmdt
```

### via release

Download the latest stable release (`.whl`) from the [release](release) page.

```bash
pip install helmdt-x.x.x-py3-none-any.whl
```

## Guiding Way

This way gives you a guiding flow to deploy your service by select options and input values.

```shell
helmdt [ACTION]
```

The `helmdt` tools will find `helmdt.yaml`, `helmdt.yml` or `helmdt.json` and load them as the profile.
If those files are all not found, an error would displayed.

### Manually specify the profile

If you want to manually specify the profile file, you could use `-f` argument. Just like:

```shell
helmdt -f profile.yaml [ACTION]
helmdt -f ../profile.yaml [ACTION]
helmdt -f /home/profile.yaml [ACTION]
```

These arguments must before the [ACTION] section.

#### -f | File

Set the profile file to use.


### Actions

#### depcheck

Check the dependencies if they were installed.

#### build

Build the docker image and push it.

The tag of the image would be like: `build-[SHORT GIT COMMIT HASH]`, for example: `build-e7f38761`.

#### apply

Apply the helm package and values. and some extra values would be passed to helm package:

- image.tag - The tag that the docker image used. It would first be checked if exists before applying.
- meta.\* - The metadata from the profile would also passed to helm.

#### link

Link the kubenetes context and store it locally (into local kubenetes configuration).

Current supported service providers: `Azure Kubenetes Services`.

## Command Line Way

By passing the arguments to `helmdt`, the `helmdt` tools would not run in guiding way. If some of the arguments are missing, it would still ask you on-demand.

```shell
helmdt link -n developers-internal
helmdt build -n stripe-worker -y --no-cache
helmdt apply -n stripe-worker -e dev -y
```

The follow arguments must be after the [ACTION] section.

### --yes | Yes

Automatically skip all the prompts and answer `yes` for them. If some of the arguments are missing, and also the `-y` specified, an error would be displayed and the tools would be terminated.

### -n/--name | Name

- For `build`, the name of the docker profile to build and push.
- For `apply`, the name of the helm package profile to apply.
- For `link`, the name of the kubenetes context.

### -e/--env | Environment

The environment to apply. This argument only used in the `apply` action.

### --no-cache | Stop using cache

bypass the `--no-cache` to `docker build`. This argument only used in the `build` action.

## Profile file structure

### \<root\>

- `kubecontexts`: ([Kubenetes Context Profile](#kubenetes-context-profile)) The contexts could be linked.
- `docker`: ([Docker Image Profile](#docker-image-profile)) The profiles for docker build and push.
- `helm`: ([Helm Package Profile](#helm-package-profile)) The profiles for helm apply.

### Kubernetes Context Profile

- `name`: (string) The short name for the kubernetes context to be link, only used in the script.
- `provider`: (string) The name of the service provider. Now we only supported:

  + `azure`: Azure kubernetes Services.

    > If you'd like to use Azure kubernetes Services, you should also specify the follow keys with the same level with `provider`.
    >
    > - `subscription`: (string) The subscription id in the azure portal.
    > - `resource_group`: (string) The resource group that the kubernetes contained.
    > - `aks_name`: (string) The name of the kubernetes service.

### Docker Image Profile

- `name`: (string) The short name for the docker profile, just used in the script.
- `image_name`: (string) The image name placed in the local and pushed to the repository.
- `repository`: (string) The address of the repository.
- `dockerfile`: (string) The Dockerfile used for building.
- `contextpath`: (string) The path of building context. If not specified, the parent folder of `dockerfile` would be used by default.

### HELM Package Profile

- `name`: (string) The short name for the helm profile, just used in the script.
- `namespace`: (string) The namespace to apply. If not exists, it would created automatically.
- `dpname`: (string) The name for the helm deployment, could be found in kubenetes/Deployment.
- `package`: (string) The path of the package.
- `environments`: (list of [Helm Environment Profile](#helm-environment-profile)) The environment entries.

### Helm Environment Profile

- `name`: (string) The short name for the environment profile, just used in the script.
- `values_file`: (string) The values file.
- `kubecontext`: (string) The name of the kubenetes context where the helm package to be applied.

### Variables

- `$(gitroot)` - Would be replated to the root path of the current git repository.

### Example

```yaml
kubecontexts:
  - name: int
    provider: azure
    subscription: xxxxxxxx-xxxx-xxxx-xxxxxxxxxxxx
    resource_group: resource-group
    aks_name: service1-int
docker:
  - name: service1
    image_name: service1
    dockerfile: $(gitroot)/docker/service1/Dockerfile
    context: $(gitroot)/src
    repository: xxx.azurecr.io
helm:
  - name: service1
    dpname: service1
    namespace: ns1
    package: $(gitroot)/helm-packages
    environments:
      - name: dev
        values_file: $(gitroot)/helm-values/dev.yaml
        kubecontext: service1-dev

      - name: prod
        values_file: $(gitroot)/helm-values/prod.yaml
        kubecontext: service1-prod
```
