from copy import deepcopy
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI
from tiktoken import encoding_for_model
from doc_test.agent.functions import (
    _get_directory_contents,
    check_presence,
    directory_contents_str,
    get_api_url,
    get_directory_contents,
    get_file_contents,
    inspect_header,
)
from doc_test.agent.functions_json import (
    FUNC_DIR,
    FUNC_FILE,
    FUNC_GUESS,
    FUNC_PRESENCE,
    FUNC_DOCKERFILE,
)
from doc_test.utils import classify_output, notify, print_output, wrap_message
from doc_test.consts import (
    DOCKERFILE_PROMPT_PATH,
    DOCKERFILE_REPAIR_PROMPT_PATH,
    NL_PROMPT_PATH,
    SYSTEM_PROMPT_PATH,
)
from vm_control import VMController


class Agent:
    def __init__(
        self,
        model: str,
        system: str,
        messages: Optional[List[Dict[str, Any]]] = None,
        count_tokens: bool = False,
        verbose: bool = True,
    ) -> None:
        self.calls = 0
        self.tokens = 0 if count_tokens else None
        self.messages = []
        self.verbose = verbose
        key = os.getenv("OPENAI_API_KEY")
        self.system = system
        self.client = OpenAI(api_key=key)
        self.model = model
        self.targets = {}
        if self.tokens is not None:
            self.encoder = encoding_for_model(model)

        self.messages = messages or [{"role": "system", "content": self.system}]

    def log(self, message: str):
        if self.verbose:
            print(message)

    @staticmethod
    def init_system_message(
        git_url: str,
        categories_path: str,
        file_path: str = SYSTEM_PROMPT_PATH,
    ) -> str:
        with open(file_path, "r") as f:
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

    def write_conversation(self, log_file: str = "logs/agent_log.txt"):
        conversation = "\n\n".join([wrap_message(message) for message in self.messages])
        with open(log_file, "w") as f:
            f.write(conversation)

    def query(self, message, tools: Optional[List[Dict[str, Any]]] = None, **kwargs):
        print_output(message, ">", self.verbose)

        self.messages.append({"role": "user", "content": message})
        response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=tools,
                tool_choice="auto" if tools is not None else None,
                **kwargs,
            )
            .choices[0]
            .message
        )

        if tools is None:
            response = response.content
            self.messages.append({"role": "assistant", "content": response})

        elif response.tool_calls is None or len(response.tool_calls) == 0:
            raise ValueError("No tools were used")
        else:
            function_name = response.tool_calls[0].function.name
            function_args = response.tool_calls[0].function.arguments
            response = {
                "id": response.tool_calls[0].id,
                "type": "function",
                "function": {
                    "name": function_name,
                    "arguments": function_args,
                },
            }
            self.messages.append(
                {
                    "role": "assistant",
                    "tool_calls": [response],
                }
            )

        print_output(str(response), "<", self.verbose)

        self.calls += 1

        if self.tokens is not None:
            if self.tokens == 0:
                self.tokens = len(self.encoder.encode(self.system))
            self.tokens += len(self.encoder.encode(message["content"])) + len(
                self.encoder.encode(response)
            )
        return response

    def classify_repo(
        self,
        repo_url: str,
        followup_path: str,
        categories_path: str,
    ):
        try:
            return self.classify_repo_loop(
                *self.classify_repo_setup(repo_url, followup_path, categories_path)
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
        followup_path: str,
        categories_path: str,
    ):
        followup, root_dir, api_url, categories = super().classify_repo_setup(
            repo_url, followup_path, categories_path
        )
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

        while response_class != "classify_repo":
            function_response = self.use_tool(
                response=response,
                response_class=response_class,
                directories=directories,
                files=files,
                file_contents=file_contents,
                tools=tools,
                api_url=api_url,
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

        function_response = {
            "tool_call_id": response["id"],
            "role": "tool",
            "name": response["function"]["name"],
            "content": "ok.",
        }
        self.messages.append(function_response)
        categories_dict = {
            i: [str(i), f"[{i}]", category] for i, category in enumerate(categories, 1)
        }
        guess = classify_output(
            str(json.loads(response["function"]["arguments"])["category"]),
            categories_dict,
        )
        self.guess = guess
        return guess

    def use_tool(
        self,
        response: str,
        response_class: str,
        directories: List[str],
        files: List[str],
        file_contents: Dict[str, Dict[str, str]],
        tools: List[Dict[str, Any]],
        api_url: str,
    ) -> str:
        match response_class:
            case "get_directory_contents":
                function_response = get_directory_contents(
                    response, directories, files, api_url, self.targets
                )
            case "get_file_contents":
                function_response = get_file_contents(
                    response, files, tools, file_contents, api_url, self.targets
                )
            case "check_presence":
                function_response = check_presence(response, api_url, self.targets)
            case "inspect_header":
                function_response = inspect_header(
                    response, files, file_contents, self.targets
                )
        return (
            function_response
            + "\n"
            + (
                "use the tools to either get more information "
                "or make a guess once you are confident."
            )
        )

    def gen_nl_description(self):
        with open(NL_PROMPT_PATH, "r") as f:
            installation = f.read()
        resp = self.query(installation, None)
        return resp

    def gen_dockerfile(self, url: str, repo_name: str = None) -> str:

        with open(DOCKERFILE_PROMPT_PATH, "r") as f:
            prompt = f.read().replace("<REPO_URL>", url)

        response = self.query(message=prompt, tools=[FUNC_DOCKERFILE])
        dockerfile = str(json.loads(response["function"]["arguments"])["dockerfile"])

        if repo_name is not None:
            with open(f"logs/dockerfiles/{repo_name}.dockerfile", "w") as f:
                f.write(dockerfile)

        function_response = {
            "tool_call_id": response["id"],
            "role": "tool",
            "name": response["function"]["name"],
            "content": "ok.",
        }
        self.messages.append(function_response)

        return dockerfile

    def test_dockerfile(
        self,
        url: str,
        dockerfile: str,
        repo_name: Optional[str] = None,
        vmc: Optional[VMController] = None,
    ) -> bool:
        dockerfile_path = "logs/dockerfiles/Dockerfile"
        name = url.split("/")[-1][:-4]

        with open(dockerfile_path, "w") as f:
            f.write(dockerfile)
        print(dockerfile)

        if vmc is None:
            logs = f"logs/build_logs/{repo_name or name}.log"
            vmc = VMController(logs)

        print(f"\nattempting to build using dockerfile, logs written to {vmc.logs}.")
        return vmc.test_dockerfile(None, dockerfile_path)

    def repair_dockerfile(
        self,
        url: str,
        dockerfile: str,
        repo_name: str,
        n_tries: int = 2,
        multiagent=False,
    ) -> bool:
        n = 0
        build_logs = f"logs/build_logs/{repo_name}-N{n}.log"
        vmc = VMController(build_logs)
        build_success = self.test_dockerfile(url, dockerfile, repo_name, vmc=vmc)

        if not build_success:
            root_dir = "\n".join(
                [
                    str(tup)
                    for tup in _get_directory_contents(
                        get_api_url(url), exclude_pyproject=False
                    )
                ]
            )
            with open(DOCKERFILE_REPAIR_PROMPT_PATH, "r") as f:
                repair_prompt = f.read().replace("<ROOT_DIRECTORY>", root_dir)
        while not build_success and n < n_tries:
            notify(f"BUILD {n} FAILED, ATTEMPTING REPAIR")
            with open(build_logs, "r") as f:
                log = f.readlines()
            sections = [i for i, l in enumerate(log) if set(l.strip()) == {"-"}]
            print(sections)
            err_msg = "\n".join(log[sections[-4] :])

            temp_repair_prompt = repair_prompt.replace("<ERROR_LOG>", err_msg)

            if multiagent:
                pass
            else:
                response = self.query(temp_repair_prompt, tools=None)
                response = self.query("", tools=[FUNC_DOCKERFILE])
                dockerfile = str(
                    json.loads(response["function"]["arguments"])["dockerfile"]
                )
                function_response = {
                    "tool_call_id": response["id"],
                    "role": "tool",
                    "name": response["function"]["name"],
                    "content": "ok.",
                }
                self.messages.append(function_response)

            n += 1
            build_logs = f"logs/build_logs/{repo_name}-N{n}.log"
            vmc = VMController(build_logs)
            build_success = self.test_dockerfile(url, dockerfile, repo_name, vmc=vmc)
        return build_success

    def save_messages(self, fname: str):
        with open(fname, "w") as f:
            json.dump(self.messages, f)
