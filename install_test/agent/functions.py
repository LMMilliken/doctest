import base64
import json
import os
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import requests

from install_test.agent.functions_json import FUNC_DICT, FUNC_HEADER
from install_test.utils import ClassificationError, classify_output, update_files_dirs

# '.rst' IS TYPICALLY FOR READMES - IT IS NL
# too much work to add support for finding .rst headers though,
# so here it is :)
NON_NL = [".py", "requirements", ".toml", ".yaml", "Dockerfile", ".lock"]


def get_api_url(git_url: str):
    "takes a git url, and returns the corresponding git api url"
    owner, repo = git_url.split("/")[-2:]
    repo = repo.replace(".git", "")
    return f"https://api.github.com/repos/{owner}/{repo}/contents"


def send_request(url: str, ref: Optional[str] = None):
    if ref is not None:
        url = url + f"?ref={ref}"
    contents_response = requests.get(
        url, headers={"Authorization": f"Bearer {os.environ.get('GIT_TOKEN')}"}
    )
    return contents_response


def get_directory_contents(
    response: str,
    directories: List[str],
    files: List[str],
    api_url: str,
    targets: Optional[Dict[str, int]] = None,
    ref: Optional[str] = None,
):
    try:
        arg = json.loads(response["function"]["arguments"])["directory"]
        target_directory = classify_output(
            arg,
            directories,
        )
    except ClassificationError:
        return (
            f"{arg} does not match any existing directories. "
            f"Please choose one of {directories}."
        )

    if targets is not None:
        key = f"DIR-{target_directory}"
        targets[key] = targets[key] + 1 if key in targets else 1

    dir_contents = _get_directory_contents(api_url, target_directory, ref=ref)
    update_files_dirs(files, directories, target_directory, dir_contents)
    function_response = (
        directory_contents_str(dir_contents)
        + "\n"
        + (f"here are the contents of directory:\n{target_directory}.")
    )
    return function_response


def _get_directory_contents(
    api_url: str,
    directory: str = "",
    exclude_pyproject: bool = True,
    ref: Optional[str] = None,
) -> List[Tuple[str, str]]:
    "return the contents of a directory in a given git repo"
    directory = "" if directory == "." or directory == "/" else directory
    contents_url = api_url + f"/{directory}"
    contents_response = send_request(contents_url, ref)

    if contents_response.status_code == 200:
        contents_data = contents_response.json()
        contents = [
            (content["name"], content["type"])
            for content in contents_data
            if not (content["name"] == "pyproject.toml" and exclude_pyproject)
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
    targets: Optional[Dict[str, int]] = None,
    ref: Optional[str] = None,
):
    args = json.loads(response["function"]["arguments"])
    try:
        target_file = classify_output(
            args["file"],
            files,
        )
    except ClassificationError:
        return f"{args['file']} does NOT exist."

    if targets is not None:
        key = f"FILE-{target_file}"
        targets[key] = targets[key] + 1 if key in targets else 1

    new_file_contents = _get_file_contents(api_url, target_file, ref=ref)
    non_nl = [x in target_file for x in NON_NL]

    headings = (
        get_headings_rst(new_file_contents)
        if target_file.endswith(".rst")
        else get_headings(new_file_contents)
    )

    if (not any(non_nl)) and headings is not None:
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
    else:
        function_response = (
            new_file_contents + "\n" + f"here are the contents of file {target_file}"
        )

    return function_response


def _get_file_contents(api_url, file_path, ref: Optional[str] = None) -> str:
    "return the contents of a file in a given git repo"
    contents_url = api_url + f"/{file_path}"
    contents_response = send_request(contents_url, ref)

    if contents_response.status_code == 200:
        file_data = contents_response.json()

        if "content" in file_data and file_data["encoding"] == "base64":

            content = base64.b64decode(file_data["content"]).decode("utf-8")
            return content


def get_headings(file: str) -> Optional[List[Tuple[str, str]]]:
    "get a list of all section heading, section content pairs from the given file"
    lines = file.split("\n")
    headings = []
    code_block = False
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith("```"):
            code_block = not code_block
        elif line.startswith("#") and not code_block:
            headings.append((line, i))
    if len(headings) == 0:
        return None

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

    sections = [("", lines[: headings[0][1]])]
    sections = sections + [
        (
            heading[0],
            "\n".join(
                lines[
                    heading[1]
                    + 1 : (headings[i + 1][1] if i + 1 < len(headings) else None)
                ]
            ),
        )
        for i, heading in enumerate(headings[:-1])
    ]
    return sections


def get_headings_rst(file: str) -> Optional[List[Tuple[str, str]]]:
    "get a list of all section heading, section content pairs from the given file"
    lines = file.split("\n")
    headings = [
        i
        for i, line in enumerate(lines[1:])
        if not line.startswith(" ")
        and line.strip() != ""
        and (all(l == "=" for l in line.strip()) or all(l == "-" for l in line.strip()))
    ]

    sections = []
    if headings[0] != 0:
        sections = [("", "\n".join(lines[: headings[0]]))]
    sections.extend(
        (lines[prev], "\n".join(lines[prev + 2 : curr]))
        for prev, curr in zip(headings, headings[1:])
    )
    return sections


def inspect_header(
    response: str,
    files: List[str],
    file_contents: Dict[str, Dict[str, str]],
    targets: Optional[Dict[str, int]] = None,
):
    args = json.loads(response["function"]["arguments"])
    try:
        target_file = classify_output(args["file"], files)
    except ClassificationError:
        return f"{args['file']} does NOT exist."

    # WHAT IF NOT???
    if target_file not in file_contents:
        return f"file {target_file} not found!"

    try:
        target_heading = classify_output(
            args["heading"], list(file_contents[target_file].keys())
        )
    except ClassificationError:
        return f"header '{args['heading']}' can not be found in file {target_file}!"

    if targets is not None:
        key = f"FILE-{target_file}"
        targets[key] = targets[key] + 1 if key in targets else 1
        key = f"{key}-HEAD-{target_heading}"
        targets[key] = targets[key] + 1 if key in targets else 1

    section_contents = file_contents[target_file][target_heading]
    function_response = (
        f"here are the contents of {target_file}'s"
        f"{target_heading} section:\n"
        f'"\n{section_contents}\n"'
    )
    return function_response


def check_presence(
    response: str,
    api_url: str,
    targets: Optional[Dict[str, int]] = None,
    ref: Optional[str] = None,
):
    target_file = json.loads(response["function"]["arguments"])["file"]

    if targets is not None:
        key = f"FILE-{target_file}"
        targets[key] = targets[key] + 1 if key in targets else 1

    exists = _check_presence(api_url, target_file, ref=ref)
    function_response = f"{target_file} does{' NOT' if not exists else ''} exist."
    return function_response


def _check_presence(api_url: str, file_path: str, ref: Optional[str] = None) -> bool:
    "check whether the provided file exists"
    contents_url = api_url + f"/{file_path}"
    contents_response = send_request(contents_url, ref)

    if contents_response.status_code == 200:
        return True
    elif contents_response.status_code == 404:
        return False


def build_default_arg(param: Dict[str, Any]):
    if "enum" in param:
        return param["enum"][0]
    match param["type"]:
        case "string":
            return ""
        case "bool":
            return True


def build_default_response(tool_name: str) -> Dict[str, Any]:
    tool = FUNC_DICT[tool_name]
    params = tool["function"]["parameters"]["properties"]
    required = tool["function"]["parameters"]["required"]
    response = {
        "role": "assistant",
        "tool_calls": {
            "id": str(uuid4()).replace("-", "")[:24],
            "type": "function",
            "function": {
                "name": tool_name,
                "arguments": json.dumps(
                    {r: build_default_arg(params[r]) for r in required}
                ),
            },
        },
    }
    return response
