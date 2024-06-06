import sys
from doc_test.consts import (
    DOCKERFILE_PROMPT_PATH,
    DOCKERFILE_STEP,
    FOLLOWUP_PROMPT_PATH,
    LIMITED,
    NL_PROMPT_PATH,
    NL_STEP,
)
from vm_control import VMController
from doc_test.agent import OpenAIAgent
from doc_test.agent.tool_using_agent import ToolUsingOpenAIAgent
from eval.agent.eval import eval
from pprint import pprint

if LIMITED:
    categories_path = "resources/python_categories_limited.json"
    repos = "eval/resources/python_repos_limited.json"
else:
    categories_path = "resources/python_categories.json"
    repos = "eval/resources/python_repos.json"


def classify_repo(
    repo_url: str, model: str = "gpt-3.5-turbo-1106"
) -> ToolUsingOpenAIAgent:

    agent = ToolUsingOpenAIAgent(
        model=model,
        system=OpenAIAgent.init_system_message(
            repo_url, categories_path=categories_path
        ),
    )
    category = agent.classify_repo(
        repo_url=repo_url,
        followup_path=FOLLOWUP_PROMPT_PATH,
        categories_path=categories_path,
    )
    pprint(agent.targets)
    return agent


def gen_nl_description(agent: ToolUsingOpenAIAgent):
    with open(NL_PROMPT_PATH, "r") as f:
        installation = f.read()
    resp = agent.query(installation, None)
    return resp


if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = "https://github.com/tiangolo/fastapi.git"
if url == "eval":
    for i in range(10):
        eval(
            categories_path=categories_path,
            followup_path=FOLLOWUP_PROMPT_PATH,
            repos=repos,
            dockerfile_step=DOCKERFILE_STEP,
        )
else:
    print(f"classifying repo: {'/'.join(url.split('/')[-2:])[:-4]}")
    agent = classify_repo(url)
    if NL_STEP:
        nl_desc = gen_nl_description(agent=agent)
        print(nl_desc)
    if DOCKERFILE_STEP:
        dockerfile = agent.gen_dockerfile(url=url)
        agent.test_dockerfile(url, dockerfile)
