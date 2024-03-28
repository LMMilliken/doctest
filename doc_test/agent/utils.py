import json

from typing import Dict, List, Optional, Union

from difflib import get_close_matches
from functools import reduce

from doc_test.agent.functions import (
    directory_contents_str,
    get_api_url,
    get_directory_contents,
)


class ClassificationError(Exception):
    def __init__(self, response: str, options: List[str]):
        message = f'response "{response}" is not similar enough to any of {options}'
        super().__init__(message)


def classify_output(
    response: str, options: Optional[Union[List[str], Dict[str, List[str]]]] = None
) -> str:
    if not options:
        return response
    elif isinstance(options, list):
        matches = get_close_matches(response, options, n=1, cutoff=0.5)
        if len(matches) == 0:
            raise ClassificationError(response, options)
        return matches[0]
    elif isinstance(options, dict):
        flattened_options = reduce(lambda acc, lst: acc + lst, options.values(), [])
        matches = get_close_matches(response, flattened_options, n=1, cutoff=0.5)
        if len(matches) == 0:
            raise ClassificationError(response, flattened_options)
        inverse_options = reduce(
            lambda acc, dct: dict(acc, **dct),
            [{value: key for value in options} for key, options in options.items()],
            {},
        )
        return inverse_options[matches[0]]
    else:
        raise ValueError(f"Invalid type for options: {type(options)}")


def init_system_message(
    git_url: str,
    file_path: str = "resources/system.md",
    categories_path: str = "resources/python_categories.json",
) -> str:
    with open(file_path, "r") as f:
        system = f.read()
    with open(categories_path, "r") as f:
        categories = json.load(f)
    contents = get_directory_contents(get_api_url(git_url))
    system = system.replace("<CONTENTS>", directory_contents_str(contents))
    system = system.replace(
        "<CATEGORIES>",
        "\n".join(
            [f" - [{i + 1}] {category}" for i, category in enumerate(categories)]
        ),
    )
    return system
