import json
import os
import random
from difflib import get_close_matches
from functools import reduce
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple, Union

import git
import requests


def print_output(msg: str, char: str, verbose: bool):
    if verbose:
        print((char * 40) + "\n" + msg + "\n" + (char * 40) + "\n")


class ClassificationError(Exception):
    def __init__(self, response: str, options: List[str]):
        message = f'response "{response}" is not similar enough to any of {options}'
        super().__init__(message)


class NoToolUsedError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


def classify_output(
    response: str,
    options: Optional[Union[List[str], Dict[str, List[str]]]] = None,
    cutoff: float = 0.5,
) -> str:
    if not options:
        return response

    elif isinstance(options, list):
        matches = get_close_matches(response, options, n=1, cutoff=cutoff)
        if len(matches) == 0:
            raise ClassificationError(response, options)
        return matches[0]

    elif isinstance(options, dict):
        flattened_options = reduce(lambda acc, lst: acc + lst, options.values(), [])
        matches = get_close_matches(response, flattened_options, n=1, cutoff=cutoff)
        if len(matches) == 0:
            raise ClassificationError(response, flattened_options)
        inverse_options = reduce(
            lambda acc, dct: dict(acc, **dct),
            [{value: key for value in options} for key, options in options.items()],
            {},
        )
        return inverse_options[matches[0]]


def update_files_dirs(
    files: List[str],
    dirs: List[str],
    dir_name: str,
    dir_contents: List[Tuple[str, str]],
) -> None:
    new_files = [f"{dir_name}/{file[0]}" for file in dir_contents if file[1] == "file"]
    new_dirs = [f"{dir_name}/{file[0]}" for file in dir_contents if file[1] == "dir"]
    files.extend(new_files)
    dirs.extend(new_dirs)


def wrap_message(message: Dict[str, Any]):
    match message["role"]:
        case "system":
            wrapped = (
                "---------" * 2 + "\n" + message["content"] + "\n" + "---------" * 2
            )
        case "user" | "tool":
            wrapped = (
                ">>>>>>>>>>" * 2 + "\n" + message["content"] + "\n" + ">>>>>>>>>>" * 2
            )
        case "assistant":
            wrapped = (
                "<<<<<<<<<<" * 2
                + "\n"
                + (
                    message["content"]
                    if "content" in message
                    else str(message["tool_calls"])
                )
                + "\n"
                + "<<<<<<<<<<" * 2
            )
        case "error":
            wrapped = (
                "XXXXXXXXXX" * 2 + "\n" + message["content"] + "\n" + "XXXXXXXXXXX" * 2
            )
        case _:
            print(message)
    return wrapped


def log_eval(repos: List[Dict[str, Any]]):
    with open("logs/eval.json", "r") as f:
        logs = json.load(f)

    repo = git.Repo(search_parent_directories=True)
    latest_commit = repo.head.commit

    commit_id = repo.head.commit.hexsha[:7]
    commit_message = latest_commit.message.strip()

    score = sum([r["correct"] for r in repos.values()])
    log = {
        "commit_id": commit_id,
        "commit_message": commit_message,
        "score": score,
        "max": len(repos),
        "repos": repos,
    }
    logs.append(log)
    with open("logs/eval.json", "w") as f:
        json.dump(logs, f)


def get_build_log_sections(log: str) -> List[List[str]]:
    lines = log.split("\n")
    sections = [i for i, l in enumerate(lines) if set(l) == {"-"}]
    prev = 0
    ret = []
    for section_end in sections:
        ret.append(lines[prev:section_end])
        prev = section_end
    ret.append(lines[prev:])


def notify(message: str, stdout=True):
    # Helper method to send experiment progress to a slack channel
    # To enable, set the SLACK_WEBHOOK environment variable to the address of a slack webhook
    # Setting this variable is not necessary to run experiments
    webhook = os.getenv("SLACK_WEBHOOK")
    try:
        requests.post(webhook, data=json.dumps({"text": message}))
    except:
        pass
    if stdout:
        print(message)


def generate_name() -> str:
    names = []

    for generation in range(1, 5):
        response = requests.get(f"https://pokeapi.co/api/v2/generation/{generation}/")
        generation_data = response.json()
        for name in generation_data["pokemon_species"]:
            names.append(name["name"])

    response = requests.get(
        "https://raw.githubusercontent.com/dariusk/corpora/master/data/words/adjs.json"
    )
    adjectives_data = response.json()
    adjectives_list = adjectives_data["adjs"]
    print(len(names))
    print(len(adjectives_list))
    return f"{random.choice(adjectives_list)}-{random.choice(names)}"


def objectify(d: Any):
    if isinstance(d, dict):
        return SimpleNamespace(**{key: objectify(val) for key, val in d.items()})
    elif isinstance(d, list):
        return [objectify(x) for x in d]
    else:
        return d
