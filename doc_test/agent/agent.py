from abc import ABC, abstractmethod
from typing import List
from openai import OpenAI
import google.generativeai as genai
from tiktoken import encoding_for_model
from pprint import pprint


class Agent(ABC):
    def __init__(self, count_tokens: bool = False) -> None:
        self.calls = 0
        self.tokens = 0 if count_tokens else None
        self.messages = []

    @abstractmethod
    def query(self, message):
        pass


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

    def query(self, message, verbose: bool = True, **kwargs):

        if verbose:
            print((">>>>>>>>>" * 4) + "\n" + message + "\n" + (">>>>>>>>>" * 4) + "\n")

        self.messages.append({"role": "user", "content": message})
        response = (
            self.client.chat.completions.create(
                model=self.model, messages=self.messages, **kwargs
            )
            .choices[0]
            .message
        )
        self.messages.append(response)
        response = response.content

        if verbose:
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


# AT SOME POINT: TRY GOOGLE AI?
class GoogleAIAgent(Agent):
    def __init__(self, system: str, model: str = "gemini-pro", **kwargs) -> None:
        super().__init__(**kwargs)
        with open("googleai_key.txt", "r") as file:
            key = file.read()
        genai.configure(api_key=key)
        self.model = genai.GenerativeModel("gemini-pro")
        with open(system, "r") as f:
            self.system = f.read()

    def query(self, usr_message: str, **kwargs):
        generation_config = genai.GenerationConfig(
            temperature=None if "temperature" not in kwargs else kwargs["temperature"]
        )
        message = self.system + "\n" + usr_message
        response = self.model.generate_content(
            message, generation_config=generation_config
        ).text
        if self.tokens is not None:
            self.tokens += self.model.count_tokens(message) + self.model.count_tokens(
                response
            )
