import json
from typing import Any, Dict, List, Tuple
import requests
import base64
import os

from doc_test.agent.utils import classify_output, update_files_dirs


FUNC_INSPECT = {
    "type": "function",
    "function": {
        "name": "inspect",
        "description": ("retrieve the contents of a given directory, or file"),
        "parameters": {
            "type": "object",
            "properties": {
                "file_or_dir": {"type": "string", "enum": ["FILE", "DIRECTORY"]},
                "path": {
                    "type": "string",
                    "description": "path to the file or directory to be inspected",
                },
            },
            "required": ["file_or_dir", "path"],
        },
    },
}
FUNC_DIR = {
    "type": "function",
    "function": {
        "name": "get_directory_contents",
        "description": (
            "retrieve the contents of a given directory, "
            "including any files and subdirectories it contains."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "The path to the directory to be inspected",
                }
            },
            "required": ["directory"],
        },
    },
}

FUNC_FILE = {
    "type": "function",
    "function": {
        "name": "get_file_contents",
        "description": ("retrieve the headings of a given file."),
        "parameters": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "The path to the file to be inspected",
                }
            },
            "required": ["file"],
        },
    },
}
FUNC_HEADER = {
    "type": "function",
    "function": {
        "name": "inspect_header",
        "description": ("retrieve the contents of a given heading in a file."),
        "parameters": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "The path to the file to be inspected",
                },
                "heading": {
                    "type": "string",
                    "description": "The name of the section header to inspect",
                },
            },
            "required": ["file", "heading"],
        },
    },
}

FUNC_GUESS = {
    "type": "function",
    "function": {
        "name": "classify_repo",
        "description": (
            "classify repo into one of the possible categories "
            "based on its installation method."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Which method of installation is used out of:\n",
                    "enum": [],
                }
            },
            "required": ["category"],
        },
    },
}

FUNC_PRESENCE = {
    "type": "function",
    "function": {
        "name": "check_presence",
        "description": (
            "Confirm whether the given files exists in the project. "
            "Use this to confirm any assumptions you make, to preven hallucinations"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "The path to the file",
                }
            },
            "required": ["file"],
        },
    },
}
NON_NL = [".py" "requirements", ".toml", ".yaml"]


def get_api_url(git_url: str):
    "takes a git url, and returns the corresponding git api url"
    owner, repo = git_url.split("/")[-2:]
    repo = repo.replace(".git", "")
    return f"https://api.github.com/repos/{owner}/{repo}/contents"


def get_directory_contents(
    response: str, directories: List[str], files: List[str], api_url: str
):

    target_directory = classify_output(
        json.loads(response["function"]["arguments"])["directory"],
        directories,
    )
    dir_contents = _get_directory_contents(api_url, target_directory)
    update_files_dirs(files, directories, target_directory, dir_contents)
    function_response = (
        directory_contents_str(dir_contents)
        + "\n"
        + (f"here are the contents of directory:\n{target_directory}.")
    )
    return function_response


def _get_directory_contents(api_url: str, directory: str = "") -> List[Tuple[str, str]]:
    "return the contents of a directory in a given git repo"
    directory = "" if directory == "." or directory == "/" else directory
    contents_url = api_url + f"/{directory}"
    contents_response = requests.get(
        contents_url, headers={"Authorization": f"Bearer {os.environ.get('GIT_TOKEN')}"}
    )

    if contents_response.status_code == 200:
        contents_data = contents_response.json()
        contents = [
            (content["name"], content["type"])
            for content in contents_data
            if content["name"] != "pyproject.toml"
        ]
    else:
        raise ValueError(
            f"Failed to retrieve contents of directory {directory} "
            f"in repository {api_url} (status code: {contents_response.status_code})"
        )

    return contents


def directory_contents_str(contents: List[Tuple[str, str]]) -> str:
    contents = sorted(contents, key=lambda x: x[1] == "file")
    return "\n".join([f"- ({c[1]}) {c[0]}" for c in contents])


def get_file_contents(
    response: str,
    files: List[str],
    tools: List[Dict[str, Any]],
    file_contents: Dict[str, Dict[str, str]],
    api_url: str,
):
    target_file = classify_output(
        json.loads(response["function"]["arguments"])["file"],
        files,
    )

    new_file_contents = _get_file_contents(api_url, target_file)
    non_nl = [x in target_file for x in NON_NL]
    print(non_nl)
    if any(non_nl):
        function_response = (
            file_contents + "\n" + f"here are the contents of file {target_file}"
        )
    else:
        headings = get_headings(new_file_contents)
        contents_dict = {h[0]: h[1] for h in headings}
        headings_str = "\n - ".join([h[0] for h in headings])
        function_response = (
            f"\nhere are the section headers of the file: \n - {headings_str}"
        )
        if len(file_contents.keys()) == 0:
            function_response += (
                "\n You can use the `inspect_header` "
                "function to see the content any file heading."
            )
            tools.append(FUNC_HEADER)
        file_contents[target_file] = contents_dict
    return function_response


def _get_file_contents(api_url, file_path) -> str:
    "return the contents of a file in a given git repo"
    contents_url = api_url + f"/{file_path}"
    contents_response = requests.get(
        contents_url, headers={"Authorization": f"Bearer {os.environ.get('GIT_TOKEN')}"}
    )

    if contents_response.status_code == 200:
        file_data = contents_response.json()

        if "content" in file_data and file_data["encoding"] == "base64":

            content = base64.b64decode(file_data["content"]).decode("utf-8")
            return content


def get_headings(file: str) -> List[Tuple[str, str]]:
    "get a list of all section heading, section content pairs from the given file"
    lines = file.split("\n")
    headings = [
        (line.strip(), i)
        for i, line in enumerate(lines)
        if line.strip().startswith("#")
    ]
    headings = [
        (
            heading[0].replace("#", "").strip(),
            heading[1],
            (
                3
                if heading[0].startswith("###")
                else 2 if heading[0].startswith("##") else 1
            ),
        )
        for heading in headings
    ]
    # Truly abhorrent.
    # There must be a better way.
    # I am so ashamed...
    sections = [("", lines[: headings[0][1]])]
    sections = sections + [
        (
            heading[0],
            "\n".join(
                lines[
                    heading[1]
                    + 1 : (
                        [h[1] for h in headings[i + 1 :] if h[2] <= heading[2]][0]
                        if i + 1 < len(headings)
                        else None
                    )
                ]
            ),
        )
        for i, heading in enumerate(headings)
    ]
    return sections


def inspect_header(
    response: str, files: List[str], file_contents: Dict[str, Dict[str, str]]
):
    args = json.loads(response["function"]["arguments"])
    target_file = classify_output(args["file"], files)
    assert target_file in file_contents
    target_heading = classify_output(
        args["heading"], list(file_contents[target_file].keys())
    )
    section_contents = file_contents[target_file][target_heading]
    function_response = (
        f"here are the contents of {target_file}'s"
        f"{target_heading} section:\n"
        f'"\n{section_contents}\n"'
    )
    return function_response


def check_presence(response: str, api_url: str):
    target_file = json.loads(response["function"]["arguments"])["file"]
    exists = _check_presence(api_url, target_file)
    function_response = f"{target_file} does{' NOT' if not exists else ''} exist."
    return function_response


def _check_presence(api_url: str, file_path: str) -> bool:
    "check whether the provided file exists"
    contents_url = api_url + f"/{file_path}"
    contents_response = requests.get(
        contents_url, headers={"Authorization": f"Bearer {os.environ.get('GIT_TOKEN')}"}
    )

    if contents_response.status_code == 200:
        return True
    elif contents_response.status_code == 404:
        return False


def search_for_term():
    # TODO
    pass
