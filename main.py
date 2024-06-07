import json
import sys
from doc_test.consts import (
    CATEGORIES_PATH,
    DEFAULT_MODEL,
    DOCKERFILE_STEP,
    FASTAPI,
    FOLLOWUP_PROMPT_PATH,
    NL_PROMPT_PATH,
    NL_STEP,
    REPOS_PATH,
)
from vm_control import VMController
from doc_test.agent import OpenAIAgent
from doc_test.agent.tool_using_agent import ToolUsingOpenAIAgent
from eval.agent.eval import eval
from pprint import pprint


def classify_repo(repo_url: str, model: str = DEFAULT_MODEL) -> ToolUsingOpenAIAgent:

    agent = ToolUsingOpenAIAgent(
        model=model,
        system=OpenAIAgent.init_system_message(
            repo_url, categories_path=CATEGORIES_PATH
        ),
    )
    category = agent.classify_repo(
        repo_url=repo_url,
        followup_path=FOLLOWUP_PROMPT_PATH,
        categories_path=CATEGORIES_PATH,
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
    url = FASTAPI
if url == "eval":
    for i in range(1):
        eval(
            categories_path=CATEGORIES_PATH,
            followup_path=FOLLOWUP_PROMPT_PATH,
            repos=REPOS_PATH,
            dockerfile_step=DOCKERFILE_STEP,
        )
else:
    # print(f"classifying repo: {'/'.join(url.split('/')[-2:])[:-4]}")
    # agent = classify_repo(url)
    # if NL_STEP:
    #     nl_desc = gen_nl_description(agent=agent)
    #     print(nl_desc)

    with open("eval/resources/messages/proxy_pool.json", "r") as f:
        dockerfile = json.load(f)

    agent = ToolUsingOpenAIAgent(DEFAULT_MODEL, None, dockerfile, verbose=True)

    if DOCKERFILE_STEP:
        # dockerfile = agent.gen_dockerfile(url=url)
        with open("eval/resources/dockerfiles/proxy_pool.dockerfile", "r") as f:
            dockerfile = f.read()
        success = agent.test_dockerfile(url, dockerfile)
        if not success:
            repo_name = url.split("/")[-1][:-4]
            agent.repair_dockerfile(url=url, dockerfile=dockerfile, repo_name=repo_name)
