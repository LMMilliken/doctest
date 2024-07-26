from copy import deepcopy
import json
import os
from typing import Any, Dict, List, Optional, Tuple, Union

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
from doc_test.agent.functions_json import FUNC_DOCKERFILE
from doc_test.utils import (
    ClassificationError,
    classify_output,
    notify,
    print_output,
    wrap_message,
)
from doc_test.consts import (
    DOCKERFILE_PROMPT_PATH,
    PER_MESSAGE_TOKEN_LIMIT,
    CLASSIFICATION_SYSTEM_PROMPT_PATH,
)


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

    def query_and_classify(
        self, message, tools, **kwargs
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        tool_names = [tool["function"]["name"] for tool in tools]
        response_class = None
        while response_class is None:
            response = self.query(message, tools, **kwargs)
            command = response["function"]["name"]
            try:
                response_class = classify_output(
                    command,
                    tool_names,
                )
            except ClassificationError:
                err_msg = (
                    f"tool {command} is not available. "
                    f"You must choose from the following tools: {', '.join(tool_names)}"
                )
                function_response = {
                    "tool_call_id": response["id"],
                    "role": "tool",
                    "name": response["function"]["name"],
                    "content": err_msg,
                }
                self.messages.append(function_response)
        return response, response_class


    def tool_loop(
        self,
        response: Dict[str, Any],
        response_class: str,          
        exit_func: str,
        directories: List[str],
        files: List[str],
        file_contents: Dict[str, Dict[str, str]],
        tools: List[Dict[str, Any]],
        api_url: str,
        followup: str,
        **kwargs
    ):
        while response_class != exit_func:
            function_response = self.use_tool(
                response=response,
                response_class=response_class,
                directories=directories,
                files=files,
                file_contents=file_contents,
                tools=tools,
                api_url=api_url,
                **kwargs
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
        return response

    def use_tool(
        self,
        response: str,
        response_class: str,
        directories: List[str],
        files: List[str],
        file_contents: Dict[str, Dict[str, str]],
        tools: List[Dict[str, Any]],
        api_url: str,
        function_response: Optional[str] = None,
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
        if len(function_response) > PER_MESSAGE_TOKEN_LIMIT:
            function_response = (
                "The content that you tried to retrieve is too large to be returned "
                "to you without risking exceeding your context window limit. "
            )
        return (
            function_response
            + "\n"
            + (
                "use the tools to either get more information "
                "or conclude your task once you are confident."
            )
        )


    def gen_dockerfile(self, url: str, repo_name: str = None) -> str:

        with open(DOCKERFILE_PROMPT_PATH, "r") as f:
            prompt = f.read().replace("<REPO_URL>", url)

        response = self.query(message=prompt, tools=[FUNC_DOCKERFILE])
        dockerfile = str(json.loads(response["function"]["arguments"])["dockerfile"])

        if repo_name is not None:
            with open(f"logs/dockerfiles/{repo_name}.dockerfile", "w") as f:
                f.write(dockerfile)

        self.confirm_tool(response)

        return dockerfile


    def confirm_tool(self, response):
        function_response = {
            "tool_call_id": response["id"],
            "role": "tool",
            "name": response["function"]["name"],
            "content": "ok.",
        }
        self.messages.append(function_response)

    def save_messages(self, fname: str, dir: Optional[str] = None):
        if dir is not None:
            os.makedirs(dir, exist_ok=True)
            fname = os.path.join(dir, fname)
        with open(fname, "w") as f:
            json.dump(self.messages, f)
