import json
import os
from typing import Any, Dict, List, Optional, Tuple

from doc_test.agent.agent import Agent
from doc_test.agent.functions import (
    _get_directory_contents,
    directory_contents_str,
    get_api_url,
)
from doc_test.agent.functions_json import (
    FUNC_DIR,
    FUNC_FILE,
    FUNC_FINISHED,
    FUNC_HEADER,
    FUNC_PRESENCE,
    FUNC_SUBMIT_FILE,
    FUNC_SUMMARISE,
)
from doc_test.consts import (
    GATHER_FOLLOWUP_PROMPT_PATH,
    GATHER_SUMMARISE_PROMPT_PATH,
    GATHER_SYSTEM_PROMPT_PATH,
)
from doc_test.utils import ClassificationError, classify_output, print_output


class GatherAgent(Agent):

    @staticmethod
    def init_system_message(
        repo_url: str, system_path: str = GATHER_SYSTEM_PROMPT_PATH
    ) -> str:
        repo_name = repo_url.split("/")[-1][:-4]
        with open(os.path.abspath(system_path), "r") as f:
            system = f.read()
        api_url = get_api_url(repo_url)
        contents = _get_directory_contents(api_url)
        system = system.replace("<CONTENTS>", directory_contents_str(contents)).replace(
            "<REPO_NAME>", repo_name
        )
        return system

    def gather(self, repo_url: str) -> Tuple[List[str], List[str]]:
        with open(GATHER_FOLLOWUP_PROMPT_PATH, "r") as f:
            followup = f.read()
        self.followup = followup.replace(
            "<SUBMIT_TOOL>", FUNC_SUBMIT_FILE["function"]["name"]
        ).replace("<FINISHED_SEARCH>", FUNC_FINISHED["function"]["name"])

        print_output(self.system + "\n", "", self.verbose)

        api_url = get_api_url(repo_url)
        root_dir = _get_directory_contents(api_url)
        tools = [FUNC_DIR, FUNC_FILE, FUNC_PRESENCE, FUNC_SUBMIT_FILE, FUNC_FINISHED]
        directories = [i[0] for i in root_dir if i[1] == "dir"] + [".", "/"]
        files = [i[0] for i in root_dir if i[1] == "file"]
        file_contents = {}
        submitted_files = []

        response, response_class = self.query_then_tool(self.followup, tools)

        response = self.tool_loop(
            response=response,
            response_class=response_class,
            exit_func=FUNC_FINISHED["function"]["name"],
            directories=directories,
            files=files,
            file_contents=file_contents,
            tools=tools,
            api_url=api_url,
            followup=self.followup,
            submitted_files=submitted_files,
        )
        self.confirm_tool(response)
        return submitted_files, file_contents

    def summarise(self, url: str, submitted_files: List[str], file_contents: List[str]):
        repo_name = url.split("/")[-1][:-4]
        with open(GATHER_SUMMARISE_PROMPT_PATH, "r") as f:
            summarise_prompt = (
                f.read()
                .replace(
                    "<TOOLS>",
                    str(
                        [FUNC_FILE["function"]["name"], FUNC_HEADER["function"]["name"]]
                    ),
                )
                .replace("<SUMMARISE_TOOL>", FUNC_SUMMARISE["function"]["name"])
                .replace("<FILES>", "\n- ".join(submitted_files))
                .replace("<REPO_NAME>", repo_name)
            )

            self.messages.append({"role": "user", "content": summarise_prompt})
            tools = [FUNC_FILE, FUNC_HEADER, FUNC_SUMMARISE]
            response, response_class = self.query_then_tool(self.followup, tools)

            response = self.tool_loop(
                response=response,
                response_class=response_class,
                exit_func=FUNC_SUMMARISE["function"]["name"],
                directories=[],
                files=submitted_files,
                file_contents=file_contents,
                tools=tools,
                api_url=get_api_url(url),
                followup=self.followup,
                submitted_files=[],
            )
        summary = json.loads(response["function"]["arguments"])["summary"]
        print_output(summary, "<", self.verbose)
        self.confirm_tool(response)
        return summary

    def use_tool(
        self,
        response: str,
        response_class: str,
        directories: List[str],
        files: List[str],
        file_contents: Dict[str, Dict[str, str]],
        tools: List[Dict[str, Any]],
        api_url: str,
        submitted_files: List[str],
    ):
        function_response = None
        if response_class == FUNC_SUBMIT_FILE["function"]["name"]:
            function_response = self.submit_file(response, files, submitted_files)
        return super().use_tool(
            response=response,
            response_class=response_class,
            directories=directories,
            files=files,
            file_contents=file_contents,
            tools=tools,
            api_url=api_url,
            function_response=function_response,
        )

    def submit_file(self, response: str, files: List[str], submitted_files: List[str]):
        args = json.loads(response["function"]["arguments"])
        try:
            target_file = classify_output(
                args["file"],
                files,
            )
            submitted_files.append(target_file)
            msg = f"{target_file} added to submitted files! Currently submitted files: {submitted_files}"
        except ClassificationError:
            msg = f"{args['file']} does NOT exist."
        return msg
