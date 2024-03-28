from typing import List, Tuple
import requests
import base64
import os


def get_api_url(git_url: str):
    "takes a git url, and returns the corresponding git api url"
    owner, repo = git_url.split("/")[-2:]
    repo = repo.replace(".git", "")
    return f"https://api.github.com/repos/{owner}/{repo}/contents"


def get_directory_contents(api_url: str, directory: str = "") -> List[Tuple[str, str]]:
    "return the contents of a directory in a given git repo"
    directory = "" if directory == "." or directory == "/" else directory
    contents_url = api_url + f"/{directory}"
    contents_response = requests.get(
        contents_url, headers={"Authorization": f"Bearer {os.environ.get('GIT_TOKEN')}"}
    )

    if contents_response.status_code == 200:
        contents_data = contents_response.json()
        contents = [(content["name"], content["type"]) for content in contents_data]
    else:
        raise ValueError(
            f"Failed to retrieve contents of directory {directory} "
            f"in repository {api_url} (status code: {contents_response.status_code})"
        )

    return contents


def directory_contents_str(contents: List[Tuple[str, str]]) -> str:
    contents = sorted(contents, key=lambda x: x[1] == "file")
    return "\n".join([f"- ({c[1]}) {c[0]}" for c in contents])


def get_file_contents(api_url, file_path) -> str:
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


def get_headings(file: str) -> List[str]:
    "get a list of all section heading, section content pairs from the given file"
    lines = file.split("\n")
    headings = [
        (line.strip(), i)
        for i, line in enumerate(lines)
        if line.strip().startswith("#")
    ]
    headings = [
        (
            heading[0],
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
            lines[
                heading[1]
                + 1 : (
                    [h[1] for h in headings[i + 1 :] if h[2] <= heading[2]][0]
                    if i + 1 < len(headings)
                    else None
                )
            ],
        )
        for i, heading in enumerate(headings)
    ]
    return sections


def search_for_term():
    # TODO
    pass
