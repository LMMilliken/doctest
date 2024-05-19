import sys
from doc_test import vm_control
from doc_test.agent import OpenAIAgent
from doc_test.agent.tool_using_agent import ToolUsingOpenAIAgent
from eval.agent.eval_classify_repo import eval_python
from pprint import pprint

LIMITED = True
NL_STEP = False
DOCKERFILE_STEP = True

if LIMITED:
    categories_path = "resources/python_categories_limited.json"
    repos = "eval/resources/python_repos_limited.json"
else:
    categories_path = "resources/python_categories.json"
    repos = "eval/resources/python_repos.json"

DOCKERFILE_PROMPT_PATH = "resources/dockerfile_prompt.md"
NL_PROMPT_PATH = "resources/installation_prompt_nl.md"


def classify_repo(
    repo_url: str, model: str = "gpt-3.5-turbo-1106"
) -> ToolUsingOpenAIAgent:

    followup_path = "resources/followup_prompt_tool_use.md"
    agent = ToolUsingOpenAIAgent(
        model=model,
        system=OpenAIAgent.init_system_message(
            repo_url, categories_path=categories_path
        ),
    )
    category = agent.classify_repo(
        repo_url=repo_url, followup_path=followup_path, categories_path=categories_path
    )
    pprint(agent.targets)
    return agent


def gen_nl_description(agent: ToolUsingOpenAIAgent):
    with open(NL_PROMPT_PATH, "r") as f:
        installation = f.read()
    resp = agent.query(installation, None)
    return resp


def gen_dockerfile(agent: ToolUsingOpenAIAgent, url: str):
    with open(DOCKERFILE_PROMPT_PATH, "r") as f:
        dockerfile_instruction = f.read().replace("<REPO_URL>", url)
    resp = agent.gen_dockerfile(dockerfile_instruction)
    return resp


if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = "https://github.com/tiangolo/fastapi.git"
if url == "eval":
    eval_python(
        categories_path=categories_path,
        followup_path=f"resources/followup_prompt_tool_use'.md",
        repos=repos,
        nl_step=NL_STEP,
        dockerfile_step=DOCKERFILE_STEP,
    )
else:
    print(f"classifying repo: {'/'.join(url.split('/')[-2:])[:-4]}")
    agent = classify_repo(url)
    if NL_STEP:
        nl_desc = gen_nl_description(agent=agent)
        print(nl_desc)
    if DOCKERFILE_STEP:
        dockerfile = gen_dockerfile(agent=agent, url=url)
        print(dockerfile)
