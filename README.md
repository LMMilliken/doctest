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