from copy import deepcopy
import json
import os
import traceback
from typing import Any, Dict, List, Tuple
from doc_test.agent.agent import Agent
from doc_test.agent.functions import (
    _get_directory_contents,
    directory_contents_str,
    get_api_url,
)
from doc_test.agent.functions_json import (
    FUNC_DIR,
    FUNC_DOCKERFILE,
    FUNC_FILE,
    FUNC_GUESS,
    FUNC_PRESENCE,
)
from doc_test.consts import (
    CLASSIFICATION_FOLLOWUP_PROMPT_PATH,
    CLASSIFICATION_SYSTEM_PROMPT_PATH,
    DOCKERFILE_PROMPT_PATH,
    NL_PROMPT_PATH,
)
from doc_test.utils import classify_output, print_output


class GenAgent(Agent):

    @staticmethod
    def init_system_message(
        git_url: str,
        categories_path: str,
        file_path: str = CLASSIFICATION_SYSTEM_PROMPT_PATH,
    ) -> str:
        with open(os.path.abspath(file_path), "r") as f:
            system = f.read()
        with open(categories_path, "r") as f:
            categories = json.load(f)
        contents = _get_directory_contents(get_api_url(git_url))
        system = system.replace("<CONTENTS>", directory_contents_str(contents))
        system = system.replace(
            "<CATEGORIES>",
            "\n".join(
                [f" - [{i + 1}] {category}" for i, category in enumerate(categories)]
            ),
        )
        return system

    def classify_repo(
        self,
        repo_url: str,
        categories_path: str,
    ):
        try:
            return self.classify_repo_loop(
                *self.classify_repo_setup(repo_url, categories_path)
            )
        except Exception as e:
            stack_trace = traceback.format_exc()
            self.messages.append(
                {
                    "role": "error",
                    "content": f"{str(type(e))[8:-2]}: {str(e)}\n{stack_trace}",
                }
            )
            raise e
        finally:
            repo_name = repo_url.split("/")[-1][:-4]
            self.write_conversation(
                log_file=f"logs/run_logs/{self.__class__.__name__}-{repo_name}.txt"
            )

    def classify_repo_setup(
        self,
        repo_url: str,
        categories_path: str,
    ):
        api_url = get_api_url(repo_url)

        root_dir = _get_directory_contents(api_url)

        with open(CLASSIFICATION_FOLLOWUP_PROMPT_PATH, "r") as f:
            followup = f.read()
        with open(categories_path, "r") as f:
            categories: List[str] = json.load(f)

        print_output(self.system + "\n", "", self.verbose)
        func_guess = deepcopy(FUNC_GUESS)
        func_guess["function"]["parameters"]["properties"]["category"]["enum"] = [
            i + 1 for i in range(len(categories))
        ]
        func_guess["function"]["parameters"]["properties"]["category"][
            "description"
        ] = func_guess["function"]["parameters"]["properties"]["category"][
            "description"
        ] + "\n".join(
            [f" - [{i + 1}] {category}" for i, category in enumerate(categories)]
        )
        tools = [FUNC_DIR, FUNC_FILE, FUNC_PRESENCE, func_guess]
        return followup, root_dir, api_url, categories, tools

    def classify_repo_loop(
        self,
        followup: str,
        root_dir: List[Tuple[str, str]],
        api_url: str,
        categories: List[str],
        tools: List[Dict[str, Any]],
    ):
        directories = [i[0] for i in root_dir if i[1] == "dir"] + [".", "/"]
        files = [i[0] for i in root_dir if i[1] == "file"]
        file_contents = {}
        self.query(followup, None)
        response, response_class = self.query_and_classify("", tools)

        response = self.tool_loop(
            response=response,
            response_class=response_class,
            exit_func=FUNC_GUESS['function']['name'],
            directories=directories,
            files=files,
            file_contents=file_contents,
            tools=tools,
            api_url=api_url,
            followup=followup
        )

        self.confirm_tool(response)
        categories_dict = {
            i: [str(i), f"[{i}]", category] for i, category in enumerate(categories, 1)
        }
        guess = classify_output(
            str(json.loads(response["function"]["arguments"])["category"]),
            categories_dict,
        )
        self.guess = guess
        return guess

    def gen_nl_description(self):
        with open(NL_PROMPT_PATH, "r") as f:
            installation = f.read()
        resp = self.query(installation, None)
        return resp
