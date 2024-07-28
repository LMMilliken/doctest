import argparse
from typing import List, Optional
import requests
import os

token = os.environ.get("GIT_TOKEN")
# Replace 'YOUR_TOKEN' with your actual GitHub API token

URL = "https://api.github.com/search/repositories"


def print_page(data, counter: int, contains: List[str]) -> int:
    for repo in data["items"]:
        if "ailearning" in repo["full_name"]:
            continue
        repo_contents_url = f"https://api.github.com/repos/{repo['full_name']}/contents"
        repo_contents_response = requests.get(repo_contents_url)
        repo_contents_response.raise_for_status()
        if repo_contents_response.status_code == 200:
            repo_contents_data = repo_contents_response.json()
            requirements_files = [
                content["name"]
                for content in repo_contents_data
                if content["type"] == "file" and content["name"] in contains
            ]
            if requirements_files:
                print((requirements_files, repo["html_url"]))
                counter -= 1
            if counter == 0:
                break
    return counter


def scrape_repos(
    max: int = 20,
    contains: List[str] = ["requirements.txt"],
    max_stars: int = 0,
    min_stars: int = 0,
    sort_by: str = "stars",
):
    if isinstance(contains, str):
        contains = [contains]
    q = "language:python"
    if max_stars != 0:
        q += f" stars:{min_stars}..{max_stars}"
    else:
        q += f" stars:>={min_stars}"
    params = {
        "q": q,
        "sort": sort_by,
        "order": "desc",
        "per_page": 100,  # Max results per page
    }

    # Prepare headers with authentication
    headers = {"Authorization": f"token {token}"}

    # Make initial request to get the first page of results
    response = requests.get(URL, headers=headers, params=params)
    response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

    # Process the first page of results
    data = response.json()
    # max = print_page(data, max, contains=contains)

    # Check if there are more pages of results
    while "next" in response.links:
        # Make subsequent requests for additional pages
        next_url = response.links["next"]["url"]
        response = requests.get(next_url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

        # Process the next page of results
        data = response.json()
        max = print_page(data, max, contains=contains)
        if max == 0:
            break


def get_repository_language(git_url: str) -> str:
    # Extract owner and repository name from the Git URL
    owner, repo = git_url.replace(".git", "").split("/")[-2:]

    # Fetch repository languages
    languages_url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    languages_response = requests.get(languages_url)
    if languages_response.status_code == 200:
        languages_data = languages_response.json()
        # Get the most used language
        most_used_language = max(languages_data, key=languages_data.get)
        return most_used_language
    else:
        print(f"Failed to retrieve languages for repository {owner}/{repo}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max_stars",
        default=0,
        help="maximum number of stars for a repo to contain",
    )
    parser.add_argument(
        "--min_stars",
        default=0,
        help="Minimum number of stars for a repo to contain",
    )
    parser.add_argument(
        "--sort_by",
        default="stars",
        help="value to order repos by",
    )
    args = parser.parse_args()
    scrape_repos(
        max=100,
        contains=["poetry.lock", "requirements.txt"],
        max_stars=int(args.max_stars),
        min_stars=int(args.min_stars),
        sort_by=args.sort_by,
    )
