import argparse
from io import TextIOWrapper
import re
import subprocess
import sys
import time
from typing import List, Optional
import uuid
from doc_test.consts import FASTAPI
from doc_test.git_scraping import get_repository_language
import os

SETUP_FILE = "resources/setup.sh"
MACHINE_NAME = "ub"
USER_NAME = "machine"
PWD = "123"
HOST_PORT = "3022"
DOCKER_NAME = "lmmilliken"
IMAGE_NAME = "temp_image"
TIMEOUT = 300


class VMController:
    def __init__(self, logs: Optional[str] = "STDOUT") -> None:
        self.logs = logs
        if self.logs is not None:
            with open(self.logs, "w") as f:
                f.write("")

    def log(self, msg, flag="a"):
        if self.logs == "STDOUT":
            print(msg)
        elif self.logs is not None:
            with open(self.logs, flag) as f:
                f.write(msg + "\n")

    def get_dockerfile(self, target_repo: str) -> str:
        """returns path to a preset dockerfile based on the langauge of target repo."""
        language = get_repository_language(target_repo).lower()
        dockerfile = os.path.abspath(
            f"resources/default_dockerfiles/{language}/Dockerfile"
        )
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
            f"sshpass -p {PWD} ssh -p {HOST_PORT} {USER_NAME}@localhost "
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
        print(repo_dir)
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

    def build_project(self, repo_dir: str, logs: str) -> bool:
        """Run docker build in the virtual machine, and stream progress."""
        # build dockerfile
        cmd = (
            f"sshpass -p {PWD} ssh -p {HOST_PORT} "
            "-oStrictHostKeyChecking=no -oUserKnownHostsFile=/dev/null "
            f"{USER_NAME}@localhost "
            f"cd {repo_dir} ; ls ; docker build --no-cache -t {IMAGE_NAME} ."
        ).split(" ")
        with open(logs, "a") as f:
            progress = self.monitor_build(cmd, f, TIMEOUT)
        #     progress = subprocess.Popen(cmd, stdout=f, stderr=f)
        # progress.wait()

        with open(logs, "r") as f:
            output = f.readlines()
        results = None
        for line in output:
            if "==" in line and " in " in line:
                results = line
        if (results is None and progress.returncode != 0) or "passed" not in results:
            err = "Error running docker build on virtual machine:\n" + "\n".join(
                [p.decode("utf-8") for p in progress.stderr]
            )
            self.log(err)
            print(err)
            return False
        else:
            succ = (
                "At least 1 test passed.\n"
                "Docker build completed successfully on virtual machine."
            )
            self.log(succ)
            print(succ)
            return True

    def monitor_build(self, cmd: List[str], f: TextIOWrapper, timeout: int):
        progress = subprocess.Popen(cmd, stdout=f, stderr=f)
        last_output_time = time.time()
        try:
            while True:
                # get latest output
                output = progress.stdout.readline()

                # check if process has finished (?)
                if output == "" and progress.poll() is not None:
                    break

                if output is not None:
                    f.write(output)
                    f.flush()
                    last_output_time = time.time()
                elif time.time() - last_output_time > timeout:
                    raise subprocess.TimeoutExpired(cmd, timeout)
            stderr_output, _ = progress.communicate()
            if stderr_output:
                f.write(stderr_output)
                f.flush()
        except subprocess.TimeoutExpired:
            progress.kill()
            f.write(f"process timedout! (took more than {timeout} seconds) Aborting...")
        finally:
            progress.wait()
        return progress

    def clear_cache(self):
        subprocess.run(
            (
                f"/usr/bin/sshpass -p {PWD} ssh -T -p {HOST_PORT} {USER_NAME}@localhost "
                f"docker system prune -a -f"
            ).split(" "),
        )

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

        with open(dockerfile, "r") as f:
            df_contents = f.read()
        self.log(df_contents, "w")

        self.open_machine()

        tmp_dir, repo_dir = self.setup_repo(target_repo, dockerfile)
        self.log("setup repo.")
        try:
            success = self.build_project(repo_dir=repo_dir, logs=logs or self.logs)
        except Exception as e:
            success = False
        except KeyboardInterrupt as e:
            success = False
        self.cleanup(tmp_dir, keep_image=keep_image, keep_repo=keep_repo)

        return success


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--dockerfile", help="path to a dockerfile you want to test")
    parser.add_argument(
        "--target_repo", help="url to a repo you want to test", default=FASTAPI
    )
    args = parser.parse_args()
    controller = VMController()
    if args.dockerfile is not None:
        repo = None
        dockerfile = args.dockerfile
    else:
        repo = args.repo
        dockerfile = None
    controller.test_dockerfile(target_repo=repo, dockerfile=dockerfile)
