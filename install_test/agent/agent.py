import json
import os
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI
from tiktoken import encoding_for_model
from tqdm import tqdm

from install_test.agent.functions import (
    build_default_response,
    check_presence,
    get_directory_contents,
    get_file_contents,
    inspect_header,
)
from install_test.agent.functions_json import FUNC_DOCKERFILE
from install_test.consts import (
    DOCKERFILE_PROMPT_PATH,
    PER_MESSAGE_TOKEN_LIMIT,
)
from install_test.utils import (
    ClassificationError,
    NoToolUsedError,
    classify_output,
    objectify,
    print_output,
    wrap_message,
)


class Agent:
    def __init__(
        self,
        model: str,
        system: str,
        messages: Optional[List[Dict[str, Any]]] = None,
        count_tokens: bool = False,
        verbose: bool = True,
        prev_messages: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        self.calls = 0
        if count_tokens:
            self._counted_messages = 0
            self._in_tokens = 0
            self._out_tokens = 0
            self._running_tokens = 0
            self.encoder = encoding_for_model(model)
        else:
            self._counted_messages = -1
            self.encoder = None
        self.messages = []
        self.verbose = verbose
        key = os.getenv("OPENAI_API_KEY")
        self.system = system
        self.client = OpenAI(api_key=key)
        self.model = model
        self.targets = {}
        self.messages = messages or [{"role": "system", "content": self.system}]
        self.prev_messages = (
            [msg for msg in prev_messages if msg["role"] == "assistant"]
            if prev_messages is not None
            else []
        )

    def log(self, message: str):
        if self.verbose:
            print(message)

    def write_conversation(self, log_file: str = "logs/agent_log.txt"):
        conversation = "\n\n".join([wrap_message(message) for message in self.messages])
        with open(log_file, "w") as f:
            f.write(conversation)

    def query(self, message, tools: Optional[List[Dict[str, Any]]] = None, **kwargs):
        print_output(message, ">", self.verbose)

        self.messages.append(
            {
                "role": "user",
                "content": message,
                "sent": True,
                "tools": tools,
            }
        )
        if len(self.prev_messages) == 3:
            print("close to the end")
        if len(self.prev_messages) > 0:
            resp = {"tool_calls": []}
            resp.update(self.prev_messages.pop(0))
            response = objectify(resp)
        else:
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
            try:
                response = response.content
                if response is not None:
                    self.messages.append({"role": "assistant", "content": response})
            except:
                pass
            raise NoToolUsedError("No tools were used")
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

        return response

    @property
    def in_tokens(self) -> Optional[int]:
        if self._counted_messages == -1:
            return None
        if self._counted_messages != len(self.messages):
            self.update_tokens()
        return self._in_tokens

    @property
    def out_tokens(self) -> Optional[int]:
        if self._counted_messages == -1:
            return None
        if self._counted_messages != len(self.messages):
            self.update_tokens()
        return self._out_tokens

    @property
    def tokens(self) -> Optional[int]:
        if self._counted_messages == -1:
            return None
        if self._counted_messages != len(self.messages):
            self.update_tokens()
        return self._running_tokens

    def update_tokens(self):
        if self._counted_messages == -1:
            return
        print("calculating token usage...")
        for message in tqdm(self.messages[self._counted_messages :]):
            # INPUTS : CUMULATIVE
            # BUT NOT ALL INPUTS (confirm function, etc.)
            # ADD 'sent' key to sent messages, see if it breaks anything
            # OUTPUTS (assistant): INDEPENDANT
            message_tokens = len(self.encoder.encode(message["role"]))
            if "content" in message:
                message_tokens += len(self.encoder.encode((message["content"])))
            if message["role"] == ["assistant"] and "tool_calls" in message:
                # I DONT KNOW HOW EXACTLY THE TOOLS ARE COUNTED. GOOD ENOUGH??!?!
                message_tokens += len(
                    self.encoder.encode(json.dumps(message["tool_calls"]["function"]))
                )
            if "tools" in message:
                # SAME AS ABOVE
                message_tokens += len(self.encoder.encode(json.dumps(message["tools"])))
            self._running_tokens += message_tokens

            if message["role"] == "user" and "sent" in message:
                self._in_tokens += self._running_tokens
            if message["role"] == "assistant":
                self._out_tokens += message_tokens
            self._counted_messages += 1
        assert self._counted_messages == len(self.messages)

    def query_and_classify(
        self, message, tools, **kwargs
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        tool_names = [tool["function"]["name"] for tool in tools]
        response_class = None
        while response_class is None:
            try:
                response = self.query(message, tools, **kwargs)
                command = response["function"]["name"]
                response_class = classify_output(
                    command,
                    tool_names,
                )
            except Exception as e:
                if isinstance(e, ClassificationError):
                    err_msg = (
                        f"tool {command} is not available. "
                        f"You must choose from the following tools: {', '.join(tool_names)}"
                    )
                else:
                    raise e
                function_response = {
                    "tool_call_id": response["id"],
                    "role": "tool",
                    "name": response["function"]["name"],
                    "content": err_msg,
                }
                self.messages.append(function_response)
        return response, response_class

    def query_then_tool(self, prompt, tools):
        if prompt is not None:
            response = self.query(prompt, None)
        try:
            tool_response, response_class = self.query_and_classify(
                "Now, use the tool that you planned to use.", tools
            )
        except NoToolUsedError:
            tool_response, response_class = None, None
        if response_class is None:
            last_line = list(response.split("\n"))[-1]
            for tool in tools:
                if tool["function"]["name"] in last_line:
                    response_class = tool["function"]["name"]
                    tool_response = build_default_response(response_class)
                    break
        return tool_response, response_class

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
        ref: Optional[str] = None,
        **kwargs,
    ):
        while response_class != exit_func:
            if response_class is not None:
                function_response = self.use_tool(
                    response=response,
                    response_class=response_class,
                    directories=directories,
                    files=files,
                    file_contents=file_contents,
                    tools=tools,
                    api_url=api_url,
                    ref=ref,
                    **kwargs,
                )

                print_output(function_response, "^", self.verbose)

                function_response = {
                    "tool_call_id": response["id"],
                    "role": "tool",
                    "name": response["function"]["name"],
                    "content": function_response,
                }
                self.messages.append(function_response)
                message = followup
            else:
                message = None
            response, response_class = self.query_then_tool(message, tools)
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
        ref: Optional[str] = None,
    ) -> str:
        try:
            match response_class:
                case "get_directory_contents":
                    function_response = get_directory_contents(
                        response, directories, files, api_url, self.targets, ref=ref
                    )
                case "get_file_contents":
                    function_response = get_file_contents(
                        response,
                        files,
                        tools,
                        file_contents,
                        api_url,
                        self.targets,
                        ref=ref,
                    )
                case "check_presence":
                    function_response = check_presence(
                        response, api_url, self.targets, ref=ref
                    )
                case "inspect_header":
                    function_response = inspect_header(
                        response, files, file_contents, self.targets
                    )
        except KeyError as e:
            function_response = (
                "Error! Make sure you provide a valid argument for every parameter."
                f"Missing parameter: {e}"
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

    def gen_dockerfile(self, url: str, repo_name: Optional[str] = None) -> str:

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
