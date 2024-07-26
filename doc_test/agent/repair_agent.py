import json
import os
from typing import Any, Dict, List, Literal, Tuple
from doc_test.agent.functions import _get_directory_contents, get_api_url
from doc_test.agent.functions_json import (
    FUNC_DIR,
    FUNC_DOCKERFILE,
    FUNC_FILE,
    FUNC_FIXABLE,
    FUNC_HEADER,
    FUNC_PRESENCE,
)
from doc_test.agent.gen_agent import GenAgent
from doc_test.consts import (
    DOCKERFILE_DIAGNOSIS_PROMPT_PATH,
    DOCKERFILE_FAILURE_FOLLOWUP_PROMPT_PATH,
    DOCKERFILE_FAILURE_PROMPT_PATH,
    DOCKERFILE_REPAIR_HINTS_PATH,
    DOCKERFILE_REPAIR_PROMPT_PATH,
    DOCKERFILE_REPAIR_SYSTEM_PROMPT_PATH,
)
from doc_test.utils import notify, print_output
from vm_control import VMController, test_dockerfile

ERR_MESSAGE_LIMIT = 30


class RepairAgent(GenAgent):

    @staticmethod
    def init_system_message(
        git_url: str,
        dockerfile: str,
        file_path: str = DOCKERFILE_REPAIR_SYSTEM_PROMPT_PATH,
    ) -> str:
        with open(file_path, "r") as f:
            system = (
                f.read()
                .replace("<DOCKERFILE>", dockerfile)
                .replace("<REPO_URL>", git_url)
            )
        return system

    def __init__(
        self,
        model: str,
        system: str,
        messages: List[Dict[str, Any]] | None = None,
        count_tokens: bool = False,
        verbose: bool = True,
    ) -> None:
        super().__init__(model, system, messages, count_tokens, verbose)
        with open(DOCKERFILE_REPAIR_HINTS_PATH, "r") as f:
            self.hints = f.read()

    def repair_dockerfile(
        self,
        url: str,
        dockerfile: str,
        repo_name: str,
        n_tries: int = 2,
    ) -> Tuple[Literal["success", "failure", "insufficient"], int]:

        build_logs_dir = "logs/build_logs"
        for file in os.listdir(build_logs_dir):
            if repo_name in file:
                os.remove(os.path.join(build_logs_dir, file))
        n = 0
        build_logs = os.path.join(build_logs_dir, f"{repo_name}-N{n}.log")
        vmc = VMController(build_logs)
        build_success = test_dockerfile(url, dockerfile, repo_name, vmc=vmc)

        if not build_success:
            root_dir = "\n".join(
                [
                    str(tup)
                    for tup in _get_directory_contents(
                        get_api_url(url), exclude_pyproject=False
                    )
                ]
            )
            self.hints = self.hints.replace("<ROOT_DIRECTORY>", root_dir)
            with open(DOCKERFILE_REPAIR_PROMPT_PATH, "r") as f:
                repair_prompt = f.read().replace("<REPAIR_HINTS>", self.hints)
        while not build_success and n < n_tries:
            notify(f"BUILD {n} FAILED, ATTEMPTING REPAIR")
            err_msg = self.get_err_msg(build_logs)

            # Check if fixable
            fixable = self.diagnosis(err_msg, url)
            if not fixable:
                return "insufficient", n

            # Suggest repair
            response = self.query(repair_prompt, tools=None)

            # Submit repaired dockerfile
            response = self.query("", tools=[FUNC_DOCKERFILE])
            self.confirm_tool(response)
            dockerfile = str(
                json.loads(response["function"]["arguments"])["dockerfile"]
            )
            n += 1
            build_logs = f"logs/build_logs/{repo_name}-N{n}.log"
            vmc = VMController(build_logs)
            build_success = test_dockerfile(url, dockerfile, repo_name, vmc=vmc)

        if not build_success:
            err_msg = self.get_err_msg(build_logs)
            fixable = self.diagnosis(err_msg=err_msg, url=url)
            return ("failure" if fixable else "insufficient"), n
        return "success", n

    def get_err_msg(self, build_logs: str):
        with open(build_logs, "r") as f:
            log = f.readlines()
        sections = [i for i, l in enumerate(log) if set(l.strip()) == {"-"}]
        if len(sections) >= 4:
            err_msg = "\n".join(log[sections[-4] :])
        else:
            err_msg = "\n".join(log[-ERR_MESSAGE_LIMIT:])
        return err_msg

    def diagnosis(self, err_msg: str, url: str) -> bool:
        root_dir = [
            tup
            for tup in _get_directory_contents(
                get_api_url(url), exclude_pyproject=False
            )
        ]

        with open(DOCKERFILE_DIAGNOSIS_PROMPT_PATH, "r") as f:
            diagnosis_prompt = (
                f.read()
                .replace("<ERROR_LOG>", err_msg)
                .replace("<REPAIR_HINTS>", self.hints)
            )
        self.query(
            diagnosis_prompt,
            tools=None,
        )

        tools = [FUNC_DIR, FUNC_FILE, FUNC_PRESENCE, FUNC_FIXABLE]
        tool_names = [tool["function"]["name"] for tool in tools]
        with open(DOCKERFILE_FAILURE_PROMPT_PATH, "r") as f:
            search_prompt = (
                f.read()
                .replace("<FIXABLE_TOOL>", FUNC_FIXABLE["function"]["name"])
                .replace(
                    "<SEARCH_TOOLS>",
                    ", ".join(tool_names),
                )
            )
        followup = search_prompt
        self.query(followup, None)
        response, response_class = self.query_and_classify("", tools)
        directories = [i[0] for i in root_dir if i[1] == "dir"] + [".", "/"]
        files = [i[0] for i in root_dir if i[1] == "file"]
        file_contents = {}

        with open(DOCKERFILE_FAILURE_FOLLOWUP_PROMPT_PATH, "r") as f:
            followup = (
                f.read()
                .replace("<FIXABLE_TOOL>", FUNC_FIXABLE["function"]["name"])
                .replace(
                    "<SEARCH_TOOLS>",
                    ", ".join(tool_names),
                )
            )

        response = self.tool_loop(
            response=response,
            response_class=response_class,
            exit_func=FUNC_FIXABLE['function']['name'],
            directories=directories,
            files=files,
            file_contents=file_contents,
            tools=tools,
            api_url=get_api_url(url),
            followup=followup
        )

        fixable = json.loads(response["function"]["arguments"])["fixable"]
        self.confirm_tool(response)

        return fixable
