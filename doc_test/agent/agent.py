from abc import ABC, abstractmethod
from copy import deepcopy
import json
from typing import Any, Dict, List, Tuple
from openai import OpenAI
from tiktoken import encoding_for_model
from pprint import pprint
import traceback

from doc_test.agent.functions import (
    FUNC_PRESENCE,
    _get_directory_contents,
    check_presence,
    directory_contents_str,
    get_api_url,
    get_directory_contents,
    get_file_contents,
    FUNC_DIR,
    FUNC_FILE,
    FUNC_GUESS,
    get_headings,
    inspect_header,
)
from doc_test.agent.utils import (
    classify_output,
    ClassificationError,
    update_files_dirs,
    wrap_message,
)


class Agent(ABC):
    def __init__(self, count_tokens: bool = False, verbose: bool = True) -> None:
        self.calls = 0
        self.tokens = 0 if count_tokens else None
        self.messages = []
        self.verbose = verbose

    @abstractmethod
    def query(self, message):
        pass

    def log(self, message: str):
        if self.verbose:
            print(message)

    def classify_repo_setup(
        self,
        repo_url: str,
        followup_path: str,
        categories_path: str,
    ):
        api_url = get_api_url(repo_url)

        root_dir = _get_directory_contents(api_url)

        with open(followup_path, "r") as f:
            followup = f.read()
        with open(categories_path, "r") as f:
            categories: List[str] = json.load(f)

        if self.verbose:
            print(self.system + "\n\n")
        return followup, root_dir, api_url, categories

    @staticmethod
    def init_system_message(
        git_url: str,
        categories_path: str,
        file_path: str = "resources/system.md",
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


class OpenAIAgent(Agent):
    def __init__(self, model: str, system: str, **kwargs) -> None:
        super().__init__(**kwargs)
        with open("openai_key.txt", "r") as file:
            key = file.read()
        self.system = system
        self.client = OpenAI(api_key=key)
        self.model = model
        if self.tokens is not None:
            self.encoder = encoding_for_model(model)

        self.messages = [{"role": "system", "content": self.system}]

    def write_conversation(self, log_file: str = "logs/agent_log.txt"):
        conversation = "\n\n".join([wrap_message(message) for message in self.messages])
        with open(log_file, "w") as f:
            f.write(conversation)

    def query(self, message, **kwargs) -> str:

        if self.verbose:
            print((">>>>>>>>>" * 4) + "\n" + message + "\n" + (">>>>>>>>>" * 4) + "\n")

        self.messages.append({"role": "user", "content": message})
        response = (
            self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                **kwargs,
            )
            .choices[0]
            .message
        )
        response = response.content
        self.messages.append({"role": "assistant", "content": response})

        if self.verbose:
            print(
                ("<<<<<<<<<<<" * 4)
                + "\n"
                + response
                + "\n"
                + ("<<<<<<<<<<<" * 4)
                + "\n"
            )

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

    def classify_repo_loop(
        self,
        followup: str,
        root_dir: List[Tuple[str, str]],
        api_url: str,
        categories: List[str],
    ):

        response = self.query(followup)
        command = response.split("\n")[-1].replace("COMMAND: ", "")
        if self.verbose:
            print("extracted command: " + command + "\n\n")
        response_class = classify_output(command[:5], ["DIR", "FILE", "GUESS"])

        while response_class != "GUESS":
            match response_class:
                case "DIR":
                    directories = [i[0] for i in root_dir if i[1] == "dir"] + [".", "/"]
                    target_directory = classify_output(command[4:], directories)
                    dir_contents = get_directory_contents(api_url, target_directory)
                    update_files_dirs(
                        files, directories, target_directory, dir_contents
                    )
                    message = (
                        f"here are the contents of directory {target_directory}:"
                        f"\n{directory_contents_str(dir_contents)}"
                    )

                case "FILE":
                    files = [i[0] for i in root_dir if i[1] == "file"]
                    try:
                        target_file = classify_output(command[5:], files)
                        file_contets = get_file_contents(api_url, target_file)
                        message = (
                            f"here are the contents of the file {target_file}:"
                            f"\n{file_contets}"
                        )
                    except ClassificationError:
                        message = f"file {command[5:]} not found."

            response = self.query(message)
            command = response.split("\n")[-1].replace("COMMAND: ", "")
            response_class = classify_output(command[:5], ["DIR", "FILE", "GUESS"])

        if response_class == "GUESS":
            categories_dict = {
                i: [str(i), f"[{i}]", category] for i, category in enumerate(categories)
            }
            guess = classify_output(command[6:], categories_dict)
            return guess


class ToolUsingOpenAIAgent(OpenAIAgent):

    def query(self, message, tools, **kwargs):
        if self.verbose:
            print((">>>>>>>>>" * 4) + "\n" + message + "\n" + (">>>>>>>>>" * 4) + "\n")

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
            response = (
                self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    **kwargs,
                )
                .choices[0]
                .message
            )
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

        if self.verbose:
            print(
                ("<<<<<<<<<<<" * 4)
                + "\n"
                + str(response)
                + "\n"
                + ("<<<<<<<<<<<" * 4)
                + "\n"
            )

        self.calls += 1

        if self.tokens is not None:
            if self.tokens == 0:
                self.tokens = len(self.encoder.encode(self.system))
            self.tokens += len(self.encoder.encode(message["content"])) + len(
                self.encoder.encode(response)
            )
        return response

    def query_and_classify(self, message, tools, **kwargs):
        response = self.query(message, tools, **kwargs)
        command = response["function"]["name"]
        response_class = classify_output(
            command,
            [tool["function"]["name"] for tool in tools],
        )
        return response, response_class

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
            if self.verbose:
                print(
                    "^^^^^^^^^" * 2 + "\n" + function_response + "\n" + "^^^^^^^^^" * 2
                )

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
            "content": "ok!",
        }
        self.messages.append(function_response)
        categories_dict = {
            i: [str(i), f"[{i}]", category] for i, category in enumerate(categories, 1)
        }
        guess = classify_output(
            str(json.loads(response["function"]["arguments"])["category"]),
            categories_dict,
        )
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
                    response, directories, files, api_url
                )
            case "get_file_contents":
                function_response = get_file_contents(
                    response, files, tools, file_contents, api_url
                )
            case "check_presence":
                function_response = check_presence(response, api_url)
            case "inspect_header":
                function_response = inspect_header(response, files, file_contents)
        return (
            function_response
            + "\n"
            + (
                "use the tools to either get more information "
                "or make a guess once you are confident."
            )
        )
