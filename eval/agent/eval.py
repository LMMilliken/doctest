import os
import sys
import json
from doc_test.agent.utils import log_eval
from doc_test.consts import DOCKERFILE_PROMPT_PATH
from doc_test.vm_control import VMController
import pytest
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
    model: str = "gpt-3.5-turbo-1106",
    dockerfile_step: bool = False,
):
    test_cases = load_test_cases(repos)
    with open("resources/system.md", "r") as f:
        system = f.read()
    with open(categories_path, "r") as f:
        category_descriptions = json.load(f)
    score = 0
    record = {}

    for test in test_cases:

        url = test["url"]
        repo_name = url.split("/")[-1][:-4]
        categories = test["categories"]
        print(f"\n\nREPO: {url}")

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
            eval_build_project(agent, repo_name, record, url)

    print(f"Evaluation complete.")
    print(f"classified {score} / {len(test_cases)} correctly")

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

    with open(DOCKERFILE_PROMPT_PATH, "r") as f:
        dockerfile_instruction = f.read().replace("<REPO_URL>", url)

    try:
        response = agent.gen_dockerfile(dockerfile_instruction, fname=repo_name)
    except Exception as e:
        print(agent.messages)
        raise e
    record[repo_name]["dockerfile"] = response

    dockerfile_path = "logs/dockerfiles/Dockerfile"
    log_path = f"logs/dockerfiles/{repo_name}.dockerfile"
    with open(dockerfile_path, "w") as f:
        f.write(response)
    with open(log_path, "w") as f:
        f.write(response)
    logs = f"logs/build_logs/{repo_name}.log"

    print(f"attempting to build using dockerfile, logs written to {logs}.")
    vmc = VMController(logs)
    build_success = vmc.test_dockerfile(None, dockerfile_path, logs=logs)

    record[repo_name]["build_success"] = build_success
