import subprocess
import sys
from typing import Optional
import uuid
from doc_test.git_scraping import get_repository_language
import os

SETUP_FILE = "resources/setup.sh"
MACHINE_NAME = "ub"
USER_NAME = "machine"
PWD = "123"
HOST_PORT = "3022"
DOCKER_NAME = "lmmilliken"
IMAGE_NAME = "temp_image"


class VMController:
    def __init__(self, logs: Optional[str]) -> None:
        self.logs = logs

    def log(self, msg):
        if self.logs == "STDOUT":
            print(msg)
        else:
            with open(self.logs, "a") as f:
                f.write(msg + "\n")

    def get_dockerfile(self, target_repo: str) -> str:
        """returns path to a preset dockerfile based on the langauge of target repo."""
        language = get_repository_language(target_repo).lower()
        dockerfile = os.path.abspath(f"dockerfiles/{language}/Dockerfile")
        if os.path.exists(dockerfile):
            return dockerfile
        else:
            return ValueError(f"No dockerfile found for langauge: {language}")

    def open_machine(self):
        """Opens the to use for testing, if the machine is already running, does nothing."""

        machines = subprocess.run(
            ["VBoxManage", "list", "vms"], capture_output=True
        ).stdout.decode("utf-8")

        if '"' + MACHINE_NAME + '"' not in machines:
            raise ValueError(f"no machine named {MACHINE_NAME}")
        running_machines = str(
            subprocess.run(
                ["VBoxManage", "list", "runningvms"], capture_output=True
            ).stdout
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
                self.log("started machine")
        else:
            self.log("machine already started")

    def setup_repo(self, target_repo: str, dockerfile: str):
        """
        Clones target repo in a temporary directory within the vm,
        then sends the dockerfile via scp.
        """
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
        self.log(f"TEMP DIR: {tmp_dir}")
        # clone target repo in temp directory
        resp = subprocess.run(
            (
                f"/usr/bin/sshpass -p {PWD} ssh -T -p {HOST_PORT} {USER_NAME}@localhost "
                f"cd {tmp_dir}"
                + (f"; git clone {target_repo}" if target_repo is not None else "")
            ).split(" "),
            capture_output=True,
        )
        self.log(resp.stderr.decode("utf-8").strip())
        self.log(resp.stdout.decode("utf-8").strip())

        # get name of the directory where the repo was cloned to (-4 to remove '.git')
        if target_repo is not None:
            repo_name = target_repo.split("/")[-1][:-4]
            repo_dir = f"{tmp_dir}/{repo_name}"
        else:
            repo_dir = tmp_dir

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
        return tmp_dir, repo_dir

    def build_project(self, repo_dir: str, logs: Optional[str] = None) -> bool:
        """Run docker build in the virtual machine, and stream progress."""
        # build dockerfile
        cmd = (
            f"sshpass -p {PWD} ssh -T -p {HOST_PORT} "
            "-oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null "
            # f"-o ProxyCommand=ssh -q -W localhost:2375 "
            f"{USER_NAME}@localhost "
            f"cd {repo_dir} ; docker build --no-cache -t {IMAGE_NAME} ."
        ).split(" ")
        if logs is None:
            progress = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
            )
            for line in iter(progress.stdout.readline, ""):
                break
        else:
            with open(logs, "a") as f:
                progress = subprocess.Popen(cmd, stdout=f, stderr=f)
        progress.wait()

        if progress.returncode != 0:
            err = "Error running docker build on virtual machine:\n" + "\n".join(
                [p.decode("utf-8") for p in progress.stderr]
            )
            self.log(err)
            print(err)
            return False
        else:
            succ = "Docker build completed successfully on virtual machine."
            self.log(succ)
            print(succ)
            return True

    def cleanup(self, tmp_dir: str, keep_image: bool = False, keep_repo: bool = False):
        """Delete docker image and temporary file after execution."""
        if not keep_image:
            # remove newly created docker image
            self.log("removing docker image...")
            subprocess.run(
                (
                    f"sshpass -p {PWD} ssh -T -p {HOST_PORT} {USER_NAME}@localhost "
                    f"docker image rm {IMAGE_NAME}"
                ).split(" "),
            )

        if not keep_repo:
            # clear temp directory
            self.log("clearing temp directory")
            subprocess.run(
                (
                    f"/usr/bin/sshpass -p {PWD} ssh -T -p {HOST_PORT} {USER_NAME}@localhost "
                    f"rm -rf {tmp_dir}"
                ).split(" "),
            )

    def test_dockerfile(
        self,
        target_repo: Optional[str],
        dockerfile: Optional[str] = None,
        keep_image: bool = False,
        keep_repo: bool = False,
        logs: Optional[str] = None,
    ):
        """
        Tests a dockerfile by connecting to a virtual machine,
        sending the dockerfile to the vm and then building the docker image inside the vm.
        """

        if target_repo is None and dockerfile is None:
            raise ValueError(
                "at least one of target_repo and dockerfile must be provided"
            )

        if dockerfile is None:
            dockerfile = self.get_dockerfile(target_repo)
            self.log(f"using dockerfile: {dockerfile}")

        self.open_machine()

        tmp_dir, repo_dir = self.setup_repo(target_repo, dockerfile)
        try:
            success = self.build_project(repo_dir=repo_dir, logs=logs)
        except Exception as e:
            success = False
        finally:
            self.cleanup(tmp_dir, keep_image=keep_image, keep_repo=keep_repo)

        return success


# test_dockerfile("test_file.txt", "https://github.com/LMMilliken/CS579-project.git")
# test_dockerfile(
#     "https://github.com/RoaringBitmap/RoaringBitmap.git", "dockerfiles/java/Dockerfile"
# )
# test_dockerfile("https://github.com/tiangolo/fastapi.git")
