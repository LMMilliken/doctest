import sys
from doc_test import vm_control
from doc_test.agent import OpenAIAgent, ToolUsingOpenAIAgent
from doc_test.agent.utils import init_system_message
from eval.agent.eval_classify_repo import eval_python


def classify_repo(
    repo_url: str, model: str = "gpt-3.5-turbo-1106", use_tools: bool = True
):
    if use_tools:
        agent = ToolUsingOpenAIAgent(model=model, system=init_system_message(repo_url))
    else:
        agent = OpenAIAgent(model=model, system=init_system_message(repo_url))
    return agent.classify_repo(repo_url=repo_url)


if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = "https://github.com/tiangolo/fastapi.git"
use_tools = len(sys.argv) <= 2 or sys.argv[2] == "tool"
if url == "eval":
    eval_python(use_tools=use_tools)
else:
    print(f"classifying repo: {'/'.join(url.split('/')[-2:])[:-4]}")
    classify_repo(url, use_tools=use_tools)
