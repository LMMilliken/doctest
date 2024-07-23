import os
from doc_test.agent.agent import Agent
from doc_test.agent.functions import (
    _get_directory_contents,
    directory_contents_str,
    get_api_url,
)
from doc_test.consts import GATHER_SYSTEM_PROMPT_PATH


class GatherAgent(Agent):

    @staticmethod
    def init_system_message(
        git_url: str,
        file_path: str = GATHER_SYSTEM_PROMPT_PATH,
    ) -> str:
        with open(os.path.abspath(file_path), "r") as f:
            system = f.read()
        contents = _get_directory_contents(get_api_url(git_url))
        system = system.replace("<CONTENTS>", directory_contents_str(contents))
        return system

    def gather(self):
        pass
