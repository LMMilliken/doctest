import subprocess
from typing import Optional
import uuid
from git_api import get_repository_language
import os

SETUP_FILE = "resources/setup.sh"
MACHINE_NAME = "ub"
USER_NAME = "machine"
PWD = "123"
HOST_PORT = "3022"
DOCKER_NAME = "lmmilliken"
IMAGE_NAME = "TEMP_IMAGE"


def get_dockerfile(target_repo: str) -> str:
    language = get_repository_language(target_repo).lower()
    dockerfile = os.path.abspath(f"dockerfiles/{language}/Dockefile")
    if os.path.exists(dockerfile):
        return dockerfile
    else:
        return ValueError(f"No dockerfile found for langauge: {language}")


def test_dockerfile(
    target_repo: str,
    dockerfile: Optional[str] = None,
    keep_image: bool = False,
    keep_repo: bool = False,
):
    """
    Tests a dockerfile by connecting to a virtual machine,
    sending the dockerfile to the vm and then building the docker image inside the vm.

    args:
        dockerfile (str): the path to the dockerfile to test.
    """

    machines = subprocess.run(
        ["VBoxManage", "list", "vms"], capture_output=True
    ).stdout.decode("utf-8")
    print(machines)
    if '"' + MACHINE_NAME + '"' not in machines:
        raise ValueError(f"no machine named {MACHINE_NAME}")
    running_machines = str(
        subprocess.run(["VBoxManage", "list", "runningvms"], capture_output=True).stdout
    )
    if '"' + MACHINE_NAME + '"' not in running_machines:
        response = str(
            subprocess.run(
                f"VBoxManage startvm {MACHINE_NAME} --type headless".split(" "),
                capture_output=True,
            ).stdout
        )
        if "successfully started" not in response:
            raise ValueError(f"failed to start machine")
        else:
            print("started machine")
    else:
        print("machine already started")
    # make temp directory
    cmd = (
        f"sshpass -p {PWD} ssh -T -p {HOST_PORT} {USER_NAME}@localhost "
        f"echo $(mktemp -d)"
    )
    tmp_dir = (
        subprocess.run(cmd.split(" "), capture_output=True)
        .stdout.decode("utf-8")
        .strip()
    )
    print(f"TEMP DIR: {tmp_dir}")
    # clone target repo in temp directory
    resp = subprocess.run(
        (
            f"/usr/bin/sshpass -p {PWD} ssh -T -p {HOST_PORT} {USER_NAME}@localhost "
            f"cd {tmp_dir}; git clone {target_repo}"
        ).split(" "),
        capture_output=True,
    )
    print(resp.stderr.decode("utf-8").strip())
    print(resp.stdout.decode("utf-8").strip())

    # get name of the directory where the repo was cloned to (-4 to remove '.git')
    repo_name = target_repo.split("/")[-1][:-4]
    repo_dir = f"{tmp_dir}/{repo_name}"

    # send dockerfile to vm
    subprocess.run(
        (
            f"/usr/bin/sshpass -p {PWD} "
            f"scp -P {HOST_PORT} "
            "-oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null "
            f"{dockerfile} {USER_NAME}@localhost:{repo_dir}"
        ).split(" ")
    )
    dockerfile = dockerfile.split("/")[-1]
    # build dockerfile
    progress = subprocess.Popen(
        (
            f"sshpass -p {PWD} ssh -T -p {HOST_PORT} "
            "-oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null "
            # f"-o ProxyCommand=ssh -q -W localhost:2375 "
            f"{USER_NAME}@localhost "
            f"cd {repo_dir} ; docker build -t {IMAGE_NAME} ."
        ).split(" "),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    print("building...")
    for line in progress.stdout:
        print(line.decode("utf-8").strip())

    progress.wait()

    if progress.returncode != 0:
        print("Error running docker build on virtual machine:")
        print("\n".join([p.decode("utf-8") for p in progress.stderr]))
    else:
        print("Docker build completed successfully on virtual machine.")
        print("done!")

    if not keep_image:
        # remove newly created docker image
        print("removing docker image...")
        subprocess.run(
            (
                f"sshpass -p {PWD} ssh -T -p {HOST_PORT} {USER_NAME}@localhost "
                f"docker image rm {IMAGE_NAME}"
            ).split(" "),
        )

    if not keep_repo:
        # clear temp directory
        print("clearing temp directory")
        subprocess.run(
            (
                f"/usr/bin/sshpass -p {PWD} ssh -T -p {HOST_PORT} {USER_NAME}@localhost "
                f"rm -rf {tmp_dir}"
            ).split(" "),
        )


# test_dockerfile("test_file.txt", "https://github.com/LMMilliken/CS579-project.git")
test_dockerfile(
    "dockerfiles/java/Dockerfile", "https://github.com/RoaringBitmap/RoaringBitmap.git"
)
