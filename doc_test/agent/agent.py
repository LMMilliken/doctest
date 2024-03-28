from abc import ABC, abstractmethod
import json
from typing import List
from openai import OpenAI
import google.generativeai as genai
from tiktoken import encoding_for_model
from pprint import pprint

from doc_test.agent.functions import (
    directory_contents_str,
    get_api_url,
    get_directory_contents,
    get_file_contents,
)
from doc_test.agent.utils import classify_output, ClassificationError


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

    def classify_repo(self, repo_url: str):
        api_url = get_api_url(repo_url)

        root_dir = get_directory_contents(api_url)

        with open("resources/followup_prompt.md", "r") as f:
            followup = f.read()
        with open("resources/python_categories.json", "r") as f:
            categories = json.load(f)

        if self.verbose:
            print(self.system + "\n\n")

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
        conversation = "\n\n".join(
            [
                (
                    "---------" * 2 + "\n" + message["content"] + "\n" + "---------" * 2
                    if message["role"] == "system"
                    else (
                        (
                            ">>>>>>>>>>" * 2
                            + "\n"
                            + message["content"]
                            + "\n"
                            + ">>>>>>>>>>" * 2
                        )
                        if message["role"] == "user"
                        else (
                            "<<<<<<<<<<" * 2
                            + "\n"
                            + message["content"]
                            + "\n"
                            + "<<<<<<<<<<" * 2
                        )
                    )
                )
                for message in self.messages
            ]
        )
        with open(log_file, "w") as f:
            f.write(conversation)

    def query(self, message, **kwargs):

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

    def classify_repo(self, repo_url: str):
        try:
            return super().classify_repo(repo_url)
        except Exception as e:
            raise e
        finally:
            repo_name = repo_url.split("/")[-1][:-4]
            self.write_conversation(log_file=f"logs/{repo_name}.txt")
