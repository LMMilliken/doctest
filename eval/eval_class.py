import csv
import json
import os
import sys
import time
from pprint import pprint
from typing import Any, Dict, List

from doc_test.agent.class_agent import ClassAgent
from doc_test.consts import DEFAULT_MODEL
from doc_test.utils import notify
from eval.eval import eval_build_project, eval_start, load_agent, load_test_cases
from vm_control import VMController


def eval_class_build(
    categories_path: os.PathLike,
    repos: str,
    n_eval: int,
    repair_attempts: int,
    run_name: str,
    model: str = DEFAULT_MODEL,
    eval_only: List[str] = [],
):
    test_cases, messages_dir = eval_start(repos, run_name, model, eval_only)
    test_cases = list(filter(lambda x: x["test_type"] == "pytest", test_cases))
    records = []

    for i in range(n_eval):

        records.append({})
        record = records[-1]
        for test in test_cases:
            start_time = time.time()
            agent = eval_class_build_repo(
                categories_path,
                repair_attempts,
                run_name,
                model,
                messages_dir,
                i,
                record,
                test,
            )
            duration = time.time() - start_time
            repo_name = test["url"].split("/")[-1][:-4]
            notify(f" - finished in {duration} seconds")
            record[repo_name]["duration"] = duration
        build_results = [
            r["build_status"] == "success"
            for r in record.values()
            if "build_status" in r
        ]

        notify(
            (
                f"EVAL ROUND {i} FIN:\n"
                f" - built {sum(build_results)} / {len(build_results)} successfully"
            )
        )
        if (i) % 2 == 0:
            VMController().clear_cache()

        with open(f"logs/eval/{run_name}_{agent.model}.json", "w") as f:
            json.dump(records, f)
    pprint(records)
    return records


def eval_class_build_repo(
    categories_path: os.PathLike,
    repair_attempts: int,
    run_name: str,
    model: str,
    messages_dir: os.PathLike,
    i: int,
    record: Dict[str, Any],
    test: Dict[str, Any],
):
    url = test["url"]
    repo_name = url.split("/")[-1][:-4]
    categories = test["categories"]
    with open(categories_path, "r") as f:
        category_descriptions = json.load(f)
    print(f"\n\nREPO: {url}")
    notify(f"REPO: {url}")
    messages_fname = f"{model}-{repo_name}-{i}.json"
    agent = load_agent(model, url, categories_path)
    correct = eval_classify_repo(
        agent,
        url,
        categories_path,
        category_descriptions,
        categories,
        record,
        repo_name,
    )
    agent.save_messages(messages_fname, messages_dir)
    print(agent.targets)

    if correct:
        nl_desc = agent.gen_nl_description()
        print(nl_desc)
        agent.gen_nl_description
        dockerfile = agent.gen_dockerfile(url, repo_name)
        eval_build_project(
            agent,
            dockerfile,
            repo_name,
            record,
            url,
            repair_attempts,
            run_name,
            model,
            i,
        )

    return agent


def eval_classify_repo(
    agent: ClassAgent,
    url: str,
    categories_path: str,
    category_descriptions: List[str],
    categories,
    record,
    repo_name,
):
    try:
        prediction = agent.classify_repo(
            url,
            categories_path=categories_path,
        )
        print(f" - PREDICTION: {prediction} {category_descriptions[prediction-1]}")
    except Exception as e:
        print(e)
        prediction = "X"
        exception = True
        # raise e
    print(
        (
            f" - {'O' if prediction in categories else 'X'} ({categories}: "
            f"{category_descriptions[categories[0]-1]})"
        )
    )
    print(f" - {agent.calls} calls")
    correct = prediction in categories
    record[repo_name] = {
        "correct": correct,
        "categories": categories,
        "targets": agent.targets,
    }
    return correct
