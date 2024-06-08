import os
import sys
import json
from doc_test.utils import log_eval, notify
from doc_test.consts import DEFAULT_MODEL, NL_PROMPT_PATH, SYSTEM_PROMPT_PATH
from typing import Dict, List, Union
from doc_test.agent import OpenAIAgent
from doc_test.agent.tool_using_agent import ToolUsingOpenAIAgent

sys.path.append(os.getcwd())


def load_test_cases(filename: str) -> List[Dict[str, Union[str, List[int]]]]:
    with open(filename, "r") as f:
        return json.load(f)


def load_agent(model: str, url: str, categories_path: str) -> ToolUsingOpenAIAgent:
    agent = ToolUsingOpenAIAgent(
        model=model,
        system=OpenAIAgent.init_system_message(url, categories_path=categories_path),
        verbose=False,
    )
    return agent


def eval(
    categories_path: str,
    followup_path: str,
    repos: str,
    model: str = DEFAULT_MODEL,
    dockerfile_step: bool = False,
    nl_step: bool = False,
):
    test_cases = load_test_cases(repos)
    test_cases = list(filter(lambda x: x["test_type"] == "pytest", test_cases))
    with open(categories_path, "r") as f:
        category_descriptions = json.load(f)
    score = 0
    record = {}
    notify("starting eval")

    for test in test_cases:

        url = test["url"]
        repo_name = url.split("/")[-1][:-4]
        categories = test["categories"]
        print(f"\n\nREPO: {url}")
        notify(f"REPO: {url}")
        agent = load_agent(model, url, categories_path)
        correct = eval_classify_repo(
            agent,
            url,
            categories_path,
            category_descriptions,
            categories,
            followup_path,
            record,
            repo_name,
        )
        score += correct

        print(agent.targets)

        if correct and dockerfile_step:
            if nl_step:
                with open(NL_PROMPT_PATH, "r") as f:
                    nl_prompt = f.read()
                    resp = agent.query(nl_prompt, None)
                    print(resp)
            eval_build_project(agent, repo_name, record, url)

    print(f"Evaluation complete.")
    print(f"classified {score} / {len(list(test_cases))} correctly")

    build_results = [
        r["build_success"] for r in record.values() if "build_success" in r
    ]

    print(f"built {sum(build_results)} / {len(build_results)} successfully")
    log_eval(record)


def eval_classify_repo(
    agent: ToolUsingOpenAIAgent,
    url: str,
    categories_path: str,
    category_descriptions: List[str],
    categories,
    followup_path: str,
    record,
    repo_name,
):
    try:
        prediction = agent.classify_repo(
            url,
            followup_path=followup_path,
            categories_path=categories_path,
        )
        print(f" - PREDICTION: {prediction} {category_descriptions[prediction-1]}")
    except Exception as e:
        print(e)
        prediction = "X"
        exception = True
    print(
        f" - {'O' if prediction in categories else 'X'} ({categories}: {category_descriptions[categories[0]-1]})"
    )
    print(f" - {agent.calls} calls")
    correct = prediction in categories
    record[repo_name] = {
        "correct": correct,
        "categories": categories,
        "targets": agent.targets,
    }
    return correct


def eval_build_project(agent: ToolUsingOpenAIAgent, repo_name, record, url):

    try:
        dockerfile = agent.gen_dockerfile(url, repo_name=repo_name)
    except Exception as e:
        print(agent.messages)
        raise e
    record[repo_name]["dockerfile"] = dockerfile
    agent.save_messages(f"logs/messages/{repo_name}.json")
    try:
        build_success = agent.repair_dockerfile(url, dockerfile, repo_name)
    except Exception:
        build_success = False
    record[repo_name]["build_success"] = build_success
