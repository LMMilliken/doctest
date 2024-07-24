import json
import os
from typing import Any, Dict, List, Optional
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
    FUNC_PRESENCE,
    FUNC_SUBMIT_FILE,
)
from doc_test.consts import GATHER_FOLLOWUP_PROMPT_PATH, GATHER_SYSTEM_PROMPT_PATH
from doc_test.utils import ClassificationError, classify_output, print_output


class GatherAgent(Agent):

    @staticmethod
    def init_system_message(
        repo_url: str,
    ) -> str:
        with open(os.path.abspath(GATHER_SYSTEM_PROMPT_PATH), "r") as f:
            system = f.read()
        api_url = get_api_url(repo_url)
        contents = _get_directory_contents(api_url)
        system = system.replace("<CONTENTS>", directory_contents_str(contents))
        return system

    def gather(self, repo_url: str):
        return self.gather_loop(*self.gather_setup(repo_url))

    def gather_setup(self, repo_url):
        with open(GATHER_FOLLOWUP_PROMPT_PATH, "r") as f:
            followup = f.read()
        followup = followup.replace(
            "<SUBMIT_TOOL>", FUNC_SUBMIT_FILE["function"]["name"]
        ).replace("<FINSIHED_SEARCH>", FUNC_FINISHED["function"]["name"])
        print_output(self.system + "\n", "", self.verbose)
        api_url = get_api_url(repo_url)
        root_dir = _get_directory_contents(api_url)
        return followup, root_dir, api_url

    def gather_loop(self, followup, root_dir, api_url):
        tools = [FUNC_DIR, FUNC_FILE, FUNC_PRESENCE, FUNC_SUBMIT_FILE, FUNC_FINISHED]
        directories = [i[0] for i in root_dir if i[1] == "dir"] + [".", "/"]
        files = [i[0] for i in root_dir if i[1] == "file"]
        file_contents = {}
        submitted_files = []

        self.query(followup, None)
        response, response_class = self.query_and_classify("", tools)

        while response_class != FUNC_FINISHED["function"]["name"]:
            function_response = self.use_tool(
                response=response,
                response_class=response_class,
                directories=directories,
                files=files,
                file_contents=file_contents,
                tools=tools,
                api_url=api_url,
                submitted_files=submitted_files,
            )

            print_output(function_response, "^", self.verbose)

            function_response = {
                "tool_call_id": response["id"],
                "role": "tool",
                "name": response["function"]["name"],
                "content": function_response,
            }
            self.messages.append(function_response)
            self.query(followup, None)
            response, response_class = self.query_and_classify("", tools)

        return submitted_files

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
