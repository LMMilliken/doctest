from abc import ABC, abstractmethod
from copy import deepcopy
import json
from typing import Any, Dict, List, Optional, Tuple
from openai import OpenAI
from tiktoken import encoding_for_model
from pprint import pprint
import traceback
import os
from doc_test.agent.functions_json import (
    FUNC_PRESENCE,
    FUNC_DIR,
    FUNC_FILE,
    FUNC_GUESS,
)

from doc_test.agent.functions import (
    _get_directory_contents,
    check_presence,
    directory_contents_str,
    get_api_url,
    get_directory_contents,
    get_file_contents,
    get_headings,
    inspect_header,
)
from doc_test.utils import (
    classify_output,
    ClassificationError,
    print_output,
    update_files_dirs,
    wrap_message,
)
from doc_test.consts import SYSTEM_PROMPT_PATH


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

        print_output(self.system + "\n", "", self.verbose)
        return followup, root_dir, api_url, categories

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


class OpenAIAgent(Agent):
    def __init__(
        self,
        model: str,
        system: str,
        messages: Optional[List[Dict[str, Any]]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        key = os.getenv("OPENAI_API_KEY")
        self.system = system
        self.client = OpenAI(api_key=key)
        self.model = model
        self.targets = {}
        if self.tokens is not None:
            self.encoder = encoding_for_model(model)

        self.messages = messages or [{"role": "system", "content": self.system}]

    def write_conversation(self, log_file: str = "logs/agent_log.txt"):
        conversation = "\n\n".join([wrap_message(message) for message in self.messages])
        with open(log_file, "w") as f:
            f.write(conversation)

    def query(self, message, **kwargs) -> str:

        print_output(message, ">", self.verbose)

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

        print_output(response, "<", self.verbose)

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

        print_output("extracted command: " + command, "", self.verbose)

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

    def save_messages(self, fname: str):
        with open(fname, "w") as f:
            json.dump(self.messages, f)
