import requests
import os

token = os.environ.get("GITHUB_TOKEN")
# Replace 'YOUR_TOKEN' with your actual GitHub API token

url = "https://api.github.com/search/repositories"


def print_page(data, counter: int) -> int:
    for repo in data["items"]:
        repo_contents_url = f"https://api.github.com/repos/{repo['full_name']}/contents"
        repo_contents_response = requests.get(repo_contents_url)
        if repo_contents_response.status_code == 200:
            repo_contents_data = repo_contents_response.json()
            requirements_files = [
                content["name"]
                for content in repo_contents_data
                if content["type"] == "file" and content["name"] == "requirements.txt"
            ]
            if requirements_files:
                print(repo["html_url"])
                counter -= 1
            if counter == 0:
                break
    return counter


def scrape_repos(max: int = 20):
    params = {
        # 'q': 'language:python',
        "q": "language:python",
        # 'q': 'language:python filename:requirements.txt',
        "sort": "stars",
        "order": "desc",
        "per_page": 100,  # Max results per page
    }

    # Prepare headers with authentication
    headers = {"Authorization": f"token {token}"}

    # Make initial request to get the first page of results
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

    # Process the first page of results
    data = response.json()
    print_page(data)

    # Check if there are more pages of results
    while "next" in response.links:
        # Make subsequent requests for additional pages
        next_url = response.links["next"]["url"]
        response = requests.get(next_url, headers=headers)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes

        # Process the next page of results
        data = response.json()
        max = print_page(data, max)
        if max == 0:
            break
