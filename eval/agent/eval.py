import os
from pprint import pprint
import sys
import json
from doc_test.utils import log_eval, notify
from doc_test.consts import DEFAULT_MODEL, NL_PROMPT_PATH, SYSTEM_PROMPT_PATH
from typing import Dict, List, Union
from doc_test.agent import Agent
from doc_test.agent.agent import Agent

sys.path.append(os.getcwd())


def load_test_cases(filename: str) -> List[Dict[str, Union[str, List[int]]]]:
    with open(filename, "r") as f:
        return json.load(f)


def load_agent(model: str, url: str, categories_path: str) -> Agent:
    agent = Agent(
        model=model,
        system=Agent.init_system_message(url, categories_path=categories_path),
        verbose=False,
    )
    return agent


def eval(
    categories_path: str,
    followup_path: str,
    repos: str,
    n_eval: int,
    repair_attempts: int,
    model: str = DEFAULT_MODEL,
    dockerfile_step: bool = False,
    nl_step: bool = False,
):
    print(f"EVALUATING WITH MODEL: {model}")
    test_cases = load_test_cases(repos)
    test_cases = list(filter(lambda x: x["test_type"] == "pytest", test_cases))
    with open(categories_path, "r") as f:
        category_descriptions = json.load(f)
    score = 0
    records = []
    # record[repo]:
    #   - correct:          whether classification was successful
    #   - categories        the correct categories for the repo
    #   - targets           the files targeted by the agent during classification
    #   - build_status     whether a working dockerfile was able to be built
    notify("starting eval")

    for i in range(n_eval):
        records.append({})
        record = records[-1]
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

        build_results = [
            r["build_status"] == "success"
            for r in record.values()
            if "build_status" in r
        ]

        notify(
            (
                f"EVAL ROUND {i}:\n"
                f" - built {sum(build_results)} / {len(build_results)} successfully"
            )
        )
        # summary = {
        #     repo: [record[repo]["build_status"] for record in records] for repo in test
        # }
        with open(f"logs/eval_{agent.model}.json", "w") as f:
            json.dump(records, f)
    pprint(records)
    return records


def eval_classify_repo(
    agent: Agent,
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
        # raise e
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


def eval_build_project(agent: Agent, repo_name, record, url):
    print("eval build")
    try:
        dockerfile = agent.gen_dockerfile(url, repo_name=repo_name)
        print("test_repair")
        # agent.verbose = True
        build_status = agent.repair_dockerfile(url, dockerfile, repo_name)
        notify(f"BUILD STATUS: {build_status.upper()}")
    except Exception as e:
        print(agent.messages)
        print(e)
        build_status = "failure"
        agent.save_messages(f"logs/messages/{repo_name}.json")
        # raise e
    except KeyboardInterrupt:
        build_status = "failure"

    agent.save_messages(f"logs/messages/{repo_name}.json")
    record[repo_name]["build_status"] = build_status
