from typing import Dict, List, Optional, Union
from doc_test.agent.functions import (
    directory_contents_str,
    get_api_url,
    get_directory_contents,
    get_file_contents,
)
from doc_test.agent.agent import OpenAIAgent
from difflib import get_close_matches
from functools import reduce


def classify_output(
    response: str, options: Optional[Union[List[str], Dict[str, List[str]]]] = None
) -> str:
    if not options:
        return response
    elif isinstance(options, list):
        matches = get_close_matches(response, options, n=1, cutoff=0.5)
        if len(matches) == 0:
            raise ValueError(
                f"RESPONSE {response} IS NOT SIMILAR ENOUGH TO ANY OF {options}"
            )
        return matches[0]
    elif isinstance(options, dict):
        flattened_options = reduce(lambda acc, lst: acc + lst, options.values(), [])
        matches = get_close_matches(response, flattened_options, n=1, cutoff=0.5)
        if len(matches) == 0:
            raise ValueError(
                f"RESPONSE {response} IS NOT SIMILAR ENOUGH TO ANY OF {flattened_options}"
            )
        inverse_options = reduce(
            lambda acc, dct: dict(acc, **dct),
            [{value: key for value in options} for key, options in options.items()],
            {},
        )
        return inverse_options[matches[0]]
    else:
        raise ValueError(f"Invalid type for options: {type(options)}")


def classify_repo(repo_url: str, model: str = "gpt-3.5-turbo-1106"):
    api_url = get_api_url(repo_url)

    root_dir = get_directory_contents(api_url)

    with open("resources/system.md", "r") as f:
        system = f.read()
    with open("resources/followup_prompt.md") as f:
        followup = f.read()

    system = system.replace("<CONTENTS>", directory_contents_str(root_dir))

    print(system + "\n\n")

    agent = OpenAIAgent(model, system)

    response = agent.query(followup)
    command = response.split("\n")[-1].replace("COMMAND: ", "")
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
                target_file = classify_output(command[6:], files)
                file_contets = get_file_contents(api_url, target_file)
                message = (
                    f"here are the contents of the file {target_file}:"
                    f"\n{file_contets}"
                )
            case "GUESS":
                return
        response = agent.query(message)
        command = response.split("\n")[-1].replace("COMMAND: ", "")
        print("extracted command: " + command + "\n\n")
        response_class = classify_output(command[:5], ["DIR", "FILE", "GUESS"])
