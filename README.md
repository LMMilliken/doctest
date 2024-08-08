# Automatic evaluation of installation instructions

## Setup/Installation
In order to verify the successful installation of a repository,
a dockerfile is constructed and sent to a virtual machine to be executed. \\
As such, a virtual machine is needed to make use of the code in this repository.
Create an ubuntu machine on virtual box with the following properties:
- MACHINE_NAME = "ub"
- USER_NAME = "machine"
- PWD = "123"
Additionally, docker needs to be installed on the virtual machine, and port forwarding needs to be enabled.
See [this](https://dev.to/developertharun/easy-way-to-ssh-into-virtualbox-machine-any-os-just-x-steps-5d9i) tutorial for instructions.
The host port should be `3022`.

### Instal + setup docker
Docker needs to be installed, using the steps outlined [here](https://docs.docker.com/engine/install/ubuntu/).

Then the `docker` group needs to be created and the user added to it:
```bash
sudo groupadd docker
sudo usermod -aG docker $USER
sudo systemctl restart docker
newgrp docker
sudo chmod 666 /var/run/docker.sock
```

verify that the setup was successfull by running `sudo docker run hello-world`.

### Install openssh and git
To enable ssh connection to the virtual machine, `openssh-server` also needs to be installed:
```bash
sudo apt-get install openssh-server

sudo systemctl start ssh
sudo systemctl enable ssh

```
Git also needs to be installed to clone the taget repositories:
```bash
sudo apt-get install git-all
```


## Usage
`main.py` is the entry point for all functionalities of the project.\\
Classification and dockerfile generation of a single repository can be done like so:
```bash
python main.py --repo <GIT_URL_FOR_TARGET_REPO>
```
If `repo` is not provided, the default repo, [fastapi](https://github.com/tiangolo/fastapi.git) will be targeted for classification instead.
If you wish to skip classification,

## Results
## GPT-3.5:
| repo | classification status | build status | n_tries |
| --- | --- | --- | --- |
| core | ✖✔✖ | ✖✖✖ | ✖2✖ |
| fastapi | ✖✔✔ | ✖✖~ | ✖20 |
| open-interpreter | ✖✔✖ | ✖✖✖ | ✖2✖ |
| rich | ✖✔✖ | ✖~✖ | ✖1✖ |
| spaCy | ✔✔✔ | ~~~ | 101 |
| thefuck | ✔✔✔ | ✖~✖ | 212 |
## GPT-4o
| repo | classification status | build status | n_tries |
| --- | --- | --- | --- |
| core | ✔✔✔ | ~~~ | 022 |
| fastapi | ✔✔✔ | ✔✔✖ | 010 |
| open-interpreter | ✔✔✔ | ✔✖✖ | 222 |
| rich | ✔✔✔ | ✖✖✔ | 021 |
| spaCy | ✔✔✔ | ✖✖✖ | 222 |
| thefuck | ✔✔✔ | ✖✖~ | 220 |
### formative-suicune, concentrated-nidoran-f, short-kirlia:
| repo | build_succ | avg_tries | avg_duration | avg_retrieved | avg_recall | n_relevant | build_status | n_tries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| you-get | 0/10 | 1.9 | 215.135 | 1.0 | 1.0 | 1 | ❌❌❌❌❌➖➖➖➖➖ | [2, 0, 2, 2, 0, 2, 0, 1, 0, 0] |
| sabnzbd | 1/6 | 3.0 | 391.527 | 1.0 | 1.0 | 1 | ❌➖❌❌❌✅ | [2, 2, 2, 2, 2, 2] |
| numba | 0/1 | 1.0 | 77.002 | 0.0 | 0.0 | 2 | ❌ | [0, -1] |
| keyboard | 0/12 | 1.583 | 118.053 | 0.833 | 0.417 | 2 | ❌➖❌❌➖➖➖➖➖➖➖❌ | [0, 2, 0, 0, 0, 0, 0, 0, 0, 1, 2, 2] |
| Real-ESRGAN | 0/10 | 1.7 | 593.808 | 1.0 | 1.0 | 1 | ❌❌❌➖➖➖➖➖❌➖ | [0, 2, 2, 2, 0, 0, 1, 0, 0, 0] |
| cloud-custodian | 0/2 | 2.0 | 398.842 | 0.0 | 0.0 | 1 | ❌❌ | [0, 2] |
| instructor | 0/2 | 1.0 | 160.955 | 0.0 | 0.0 | 0 | ➖➖ | [0, 0] |
| moto | 1/2 | 2.0 | 1051.455 | 1.0 | 0.333 | 3 | ✅❌ | [0, 2] |
| aim | 0/2 | 2.0 | 183.832 | 1.0 | 1.0 | 1 | ➖➖ | [1, 1] |
| NetExec | 0/7 | 1.857 | 295.243 | 0.143 | 0.143 | 1 | ❌❌➖❌❌❌❌ | [2, 2, 0, 0, 0, 2, 0] |
| open-interpreter | 0/10 | 1.4 | 448.935 | 0.7 | 0.7 | 1 | ❌❌❌❌➖➖❌➖➖➖ | [0, 2, 0, 0, 1, 0, 0, 0, 1, 0] |
| sherlock | 0/10 | 1.6 | 129.717 | 0.0 | 0.0 | 0 | ➖❌❌❌❌➖➖➖❌➖ | [2, 2, 2, 0, 0, 0, 0, 0, 0, 0] |
| modelscope | 0/2 | 2.0 | 1051.292 | 0.0 | 0.0 | 1 | ❌➖ | [0, 2] |
| opencompass | 0/7 | 1.857 | 682.125 | 1.429 | 0.714 | 2 | ➖➖➖❌❌❌❌ | [0, 2, 2, 0, 2, 0, 0] |
| proxy_pool | 0/10 | 1.2 | 159.873 | 1.0 | 0.5 | 2 | ➖❌➖➖➖❌➖➖➖➖ | [1, 0, 1, 0, 0, 0, 0, 0, 0, 0] |
| fastapi | 1/10 | 1.5 | 201.06 | 0.0 | 0.0 | 3 | ✅❌❌❌➖❌➖➖❌➖ | [1, 0, 2, 2, 0, 0, 0, 0, 0, 0] |
| thefuck | 1/10 | 1.3 | 102.926 | 2.0 | 1.0 | 2 | ❌✅❌❌➖➖➖➖➖➖ | [2, 1, 0, 0, 0, 0, 0, 0, 0, 0] |
| textual | 3/10 | 1.2 | 216.515 | 1.0 | 1.0 | 1 | ✅✅➖✅❌➖❌❌➖➖ | [0, 0, 0, 0, 2, 0, 0, 0, 0, 0] |
| spaCy | 0/10 | 1.7 | 575.036 | 1.0 | 1.0 | 1 | ❌❌❌❌❌❌❌➖❌➖ | [0, 2, 2, 2, 0, 0, 0, 1, 0, 0] |
| boto3 | 1/2 | 2.0 | 539.402 | 1.0 | 1.0 | 1 | ❌✅ | [2, 0] |
| rich | 4/10 | 1.4 | 102.356 | 1.0 | 1.0 | 1 | ✅✅✅❌✅➖➖➖➖❌ | [0, 0, 0, 0, 0, 0, 1, 0, 1, 2] |
| icloud-drive-docker | 0/7 | 1.857 | 177.606 | 0.0 | 0.0 | 0 | ❌❌❌❌❌❌❌ | [0, 2, 0, 0, 2, 2, 0] |
| Torch-Pruning | 0/6 | 2.333 | 1144.708 | 1.0 | 1.0 | 1 | ❌❌❌❌❌❌ | [2, 2, 2, 0, 0, 2] |
| nonebot2 | 2/2 | 2.0 | 176.749 | 1.0 | 1.0 | 1 | ✅✅ | [0, 2] |
| speechbrain | 0/2 | 3.0 | 1979.742 | 1.0 | 0.5 | 2 | ➖❌ | [2, 2] |
| tqdm | 1/10 | 2.0 | 153.869 | 0.0 | 0.0 | 0 | ❌❌❌➖✅➖❌➖➖➖ | [2, 2, 0, 2, 1, 0, 2, 1, 0, 0] |
| django-stubs | 5/7 | 1.286 | 219.332 | 1.0 | 1.0 | 1 | ✅✅✅✅❌✅❌ | [0, 0, 1, 1, 0, 0, 0] |
| warehouse | 0/6 | 1.0 | 201.104 | 0.0 | 0.0 | 1 | ➖➖❌❌❌❌ | [0, 0, 0, 0, 0, 0] |
| R2R | 0/6 | 2.0 | 621.837 | 0.0 | 0.0 | 0 | ❌❌❌❌❌❌ | [0, 2, 0, 0, 2, 2, -1] |
| X-AnyLabeling | 0/7 | 2.429 | 439.516 | 0.857 | 0.857 | 1 | ❌❌❌➖❌❌❌ | [2, 2, 0, 0, 2, 2, 2] |
| core | 0/10 | 1.1 | 252.327 | 0.0 | 0.0 | 0 | ➖➖❌❌➖➖➖➖➖➖ | [0, 1, 0, 0, 0, 0, 0, 0, 0, 0] |
| black | 1/10 | 1.5 | 98.512 | 0.0 | 0.0 | 1 | ❌❌❌❌✅➖➖❌❌➖ | [0, 0, 0, 0, 1, 0, 0, 2, 2, 0] |
| openpilot | 0/10 | 1.6 | 775.425 | 0.0 | 0.0 | 1 | ❌❌❌❌➖❌➖❌➖➖ | [2, 2, 0, 2, 0, 0, 0, 0, 0, 0] |
| spleeter | 3/10 | 1.2 | 276.045 | 1.0 | 1.0 | 1 | ✅✅❌✅❌➖➖➖❌➖ | [0, 0, 2, 0, 0, 0, 0, 0, 0, 0] |
| dlt | 0/6 | 1.833 | 353.786 | 0.0 | 0.0 | 0 | ❌❌❌❌❌➖ | [2, 0, 0, 2, 0, 1] |

### left-footed-kecleon:
| repo | build_succ | avg_tries | avg_duration | avg_retrieved | avg_recall | n_relevant | build_status | n_tries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Real-ESRGAN | 0/9 | 1.0 | 191.801 | 1.0 | 1.0 | 1 | ❌❌➖➖➖➖➖➖➖ | [0, 0, 0, 0, 0, 0, 0, 0, 0] |
| R2R | 1/9 | 1.556 | 648.766 | 0.0 | 0.0 | 0 | ❌✅➖➖➖❌➖❌➖ | [0, 0, 0, 0, 1, 2, 0, 2, 0] |
| fastapi | 2/9 | 1.333 | 126.88 | 0.0 | 0.0 | 3 | ✅❌✅➖➖❌➖➖➖ | [0, 2, 0, 1, 0, 0, 0, 0, 0] |
| sherlock | 0/9 | 1.222 | 96.107 | 0.0 | 0.0 | 0 | ❌❌➖➖➖➖➖➖➖ | [0, 2, 0, 0, 0, 0, 0, 0, 0] |
| sabnzbd | 0/9 | 1.667 | 305.843 | 0.889 | 0.889 | 1 | ❌❌➖➖➖❌➖➖➖ | [2, 2, 0, 0, 0, 2, 0, 0, 0] |
| spleeter | 2/9 | 1.0 | 104.655 | 0.889 | 0.889 | 1 | ✅✅➖➖➖➖➖➖➖ | [0, 0, 0, 0, 0, 0, 0, 0, 0] |
| spaCy | 0/9 | 1.222 | 163.656 | 1.0 | 1.0 | 1 | ➖➖➖➖➖➖➖➖➖ | [0, 2, 0, 0, 0, 0, 0, 0, 0] |
| X-AnyLabeling | 1/9 | 1.556 | 210.659 | 0.444 | 0.444 | 1 | ✅➖❌➖➖❌➖➖➖ | [2, 2, 0, 0, 0, 0, 0, 0, 1] |
| speechbrain | 0/8 | 1.625 | 483.308 | 0.889 | 0.444 | 2 | ❌❌➖➖➖➖➖➖ | [2, 2, -1, 0, 0, 0, 0, 1, 0] |
| you-get | 0/9 | 1.444 | 167.382 | 0.889 | 0.889 | 1 | ❌❌➖➖➖➖➖➖➖ | [2, 2, 0, 0, 0, 0, 0, 0, 0] |
| black | 1/9 | 1.889 | 140.695 | 0.0 | 0.0 | 1 | ✅❌➖➖➖❌➖➖❌ | [2, 2, 0, 0, 0, 2, 0, 0, 2] |
| dlt | 0/9 | 1.444 | 125.55 | 0.0 | 0.0 | 0 | ➖➖➖➖❌➖➖➖➖ | [2, 0, 0, 0, 2, 0, 0, 0, 0] |
| nonebot2 | 2/9 | 1.556 | 101.312 | 0.667 | 0.667 | 1 | ✅✅➖➖➖❌➖➖➖ | [1, 1, 0, 0, 0, 2, 1, 0, 0] |
| Torch-Pruning | 0/9 | 1.333 | 297.7 | 1.0 | 1.0 | 1 | ❌❌➖➖➖➖➖➖➖ | [2, 0, 0, 0, 0, 0, 0, 1, 0] |
| open-interpreter | 0/9 | 1.444 | 592.796 | 0.444 | 0.444 | 1 | ❌❌❌➖➖➖➖➖➖ | [2, 2, 0, 0, 0, 0, 0, 0, 0] |
| moto | 0/9 | 1.444 | 237.02 | 0.667 | 0.222 | 3 | ❌❌➖❌➖➖➖➖➖ | [2, 0, 0, 2, 0, 0, 0, 0, 0] |
| rich | 2/9 | 1.0 | 98.775 | 1.0 | 1.0 | 1 | ✅✅➖➖➖➖➖➖➖ | [0, 0, 0, 0, 0, 0, 0, 0, 0] |
| proxy_pool | 0/9 | 1.222 | 92.749 | 0.889 | 0.444 | 2 | ➖➖❌➖➖➖➖➖➖ | [0, 0, 2, 0, 0, 0, 0, 0, 0] |
| thefuck | 1/9 | 1.556 | 104.736 | 2.0 | 1.0 | 2 | ❌✅➖❌➖➖➖➖➖ | [0, 1, 2, 0, 1, 0, 1, 0, 0] |
| textual | 2/9 | 1.111 | 179.083 | 1.0 | 1.0 | 1 | ✅✅➖➖➖➖➖➖➖ | [0, 0, 0, 0, 1, 0, 0, 0, 0] |
| modelscope | 0/9 | 1.556 | 202.073 | 0.333 | 0.333 | 1 | ❌❌➖➖❌❌➖❌➖ | [0, 0, 0, 0, 0, 2, 1, 2, 0] |
| boto3 | 1/9 | 1.444 | 229.811 | 1.0 | 1.0 | 1 | ❌✅➖➖➖➖➖❌➖ | [2, 0, 0, 0, 0, 0, 0, 2, 0] |
| openpilot | 0/9 | 1.778 | 478.164 | 0.0 | 0.0 | 1 | ➖❌➖➖❌➖❌➖➖ | [1, 2, 0, 0, 2, 0, 2, 0, 0] |
| tqdm | 2/9 | 1.333 | 164.236 | 0.0 | 0.0 | 0 | ❌✅✅➖➖➖❌➖➖ | [2, 0, 0, 0, 1, 0, 0, 0, 0] |
| instructor | 0/9 | 1.222 | 95.579 | 0.0 | 0.0 | 0 | ➖➖➖➖➖➖➖➖❌ | [0, 0, 0, 0, 0, 0, 0, 0, 2] |
| numba | 0/9 | 1.0 | 156.92 | 0.0 | 0.0 | 2 | ❌❌❌➖➖➖➖➖➖ | [0, 0, 0, 0, 0, 0, 0, 0, 0] |
| keyboard | 0/9 | 1.333 | 84.203 | 0.778 | 0.389 | 2 | ❌➖➖➖➖➖➖➖➖ | [0, 2, 0, 1, 0, 0, 0, 0, 0] |
| opencompass | 0/7 | 2.429 | 239.411 | 1.333 | 0.667 | 2 | ❌➖❌➖❌❌❌ | [2, -1, -1, 0, 2, 0, 2, 2, 2] |
| icloud-drive-docker | 0/9 | 1.444 | 109.657 | 0.0 | 0.0 | 0 | ❌❌➖➖➖➖➖➖➖ | [2, 2, 0, 0, 0, 0, 0, 0, 0] |
| NetExec | 0/9 | 1.222 | 123.799 | 0.0 | 0.0 | 1 | ❌➖➖➖➖➖➖➖➖ | [0, 1, 0, 0, 0, 1, 0, 0, 0] |
| warehouse | 0/9 | 1.0 | 143.574 | 0.0 | 0.0 | 1 | ➖❌➖➖➖➖➖➖➖ | [0, 0, 0, 0, 0, 0, 0, 0, 0] |
| core | 0/9 | 1.667 | 337.058 | 0.0 | 0.0 | 0 | ❌➖❌➖➖❌➖➖➖ | [2, 2, 2, 0, 0, 0, 0, 0, 0] |
| django-stubs | 2/9 | 1.444 | 86.081 | 1.0 | 1.0 | 1 | ✅✅➖➖➖➖➖➖❌ | [0, 1, 0, 0, 0, 1, 0, 0, 2] |
| cloud-custodian | 0/9 | 1.667 | 169.651 | 0.0 | 0.0 | 1 | ❌❌➖➖➖➖❌➖➖ | [2, 2, 0, 0, 2, 0, 0, 0, 0] |
| aim | 0/9 | 1.778 | 143.227 | 1.0 | 1.0 | 1 | ❌➖❌➖➖➖❌➖➖ | [2, 1, 2, 0, 0, 1, 0, 1, 0] |