import csv
import json
import os
import sys
import time
from datetime import date, datetime
from pprint import pprint
from typing import Any, Dict, List, Union

from doc_test.agent.agent import Agent
from doc_test.agent.class_agent import ClassAgent
from doc_test.agent.gather_agent import GatherAgent
from doc_test.agent.repair_agent import RepairAgent
from doc_test.consts import DEFAULT_MODEL, EVAL_LOGS, NL_PROMPT_PATH
from doc_test.utils import notify
from vm_control import VMController

sys.path.append(os.getcwd())


def load_test_cases(filename: os.PathLike) -> List[Dict[str, Union[str, List[int]]]]:
    with open(filename, "r") as f:
        return json.load(f)


def load_agent(model: str, url: str, categories_path: str) -> RepairAgent:
    agent = ClassAgent(
        model=model,
        system=ClassAgent.init_system_message(url, categories_path=categories_path),
        verbose=False,
    )
    return agent


def log_eval_start(run_name: str, model: str, repos: os.PathLike):

    start_date = str(date.today())
    start_time = datetime.now().strftime("%H:%M")
    eval_set = repos.split("/")[-1]
    with open(EVAL_LOGS, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [run_name, eval_set, model, start_date, start_time, "-", "-", "-"]
        )


def log_eval_end(finsihed: bool):

    end_date = str(date.today())
    end_time = datetime.now().strftime("%H:%M")
    data = []
    with open(EVAL_LOGS, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)

    data[-1][-3] = end_date
    data[-1][-2] = end_time
    data[-1][-1] = "✅" if finsihed else "❌"
    with open(EVAL_LOGS, "w", newline="") as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)


def eval_gather_build(
    repo_sets: List[os.PathLike],
    n_eval: int,
    repair_attempts: int,
    run_name: str,
    model: str = DEFAULT_MODEL,
    eval_only: List[str] = [],
):
    print(f"RUN NAME: {run_name}")
    print(f"EVALUATING WITH MODEL: {model}")
    log_eval_start(run_name, model, "_".join(repo_sets))

    test_cases = []
    for repo_set in repo_sets:
        test_cases.extend(load_test_cases(repo_set))
    test_cases = (
        list(filter(lambda x: any(e in x["url"] for e in eval_only), test_cases))
        if len(eval_only) > 0
        else test_cases
    )

    pprint([test_case["url"] for test_case in test_cases])
    records = []
    notify("starting eval")
    messages_dir = f"logs/messages/{run_name}"
    finished = False
    try:
        for i in range(n_eval):
            records.append({})
            record = records[-1]
            for test in test_cases:
                url = test["url"]
                repo_name = test["url"].split("/")[-1][:-4]
                gather_fname = f"{model}-{repo_name}-gather-{i}.json"
                record[repo_name] = {}
                start_time = time.time()

                agent = GatherAgent(
                    model=model,
                    system=GatherAgent.init_system_message(url),
                    verbose=False,
                    count_tokens=False,
                )
                try:
                    eval_gather_repo(
                        agent, url, test["relevant_docs"], record[repo_name], repo_name
                    )
                except Exception as e:
                    print(e)
                    continue
                finally:
                    agent.save_messages(gather_fname, messages_dir)

                dockerfile = agent.gen_dockerfile(url, repo_name)
                agent.save_messages(gather_fname, messages_dir)

                eval_build_project(
                    agent,
                    dockerfile,
                    repo_name=repo_name,
                    record=record,
                    url=url,
                    repair_attempts=repair_attempts,
                    run_name=run_name,
                    model_name=model,
                    n=i,
                )

                duration = time.time() - start_time
                notify(f" - finished in {duration} seconds")
                record[repo_name]["duration"] = duration

            notify(f"EVAL ROUND {i} FIN:\n")

            with open(f"logs/eval/{run_name}_{agent.model}.json", "w") as f:
                json.dump(records, f)
        finished = True
    finally:
        with open(f"logs/eval/{run_name}_{agent.model}.json", "w") as f:
            json.dump(records, f)
        log_eval_end(finished)

    pprint(records)
    return records


def eval_gather_repo(
    agent: GatherAgent,
    url: str,
    relevant_docs: List[str],
    record: Dict[str, Any],
    repo_name: str,
):
    notify(f"REPO: {repo_name}")
    retrieved_docs, contents = agent.gather(url)
    notify(f" - COLLECTED DOCS: {retrieved_docs}")
    notify(f" - RELEVANT DOCS: {relevant_docs}")
    relevant_retrieved = set(retrieved_docs).intersection(set(relevant_docs))
    notify(f" - SCORE: {len(relevant_retrieved)}")
    record["retrieved"] = retrieved_docs
    record["relevant"] = relevant_docs
    record["recall"] = (
        len(relevant_retrieved) / len(relevant_docs) if len(relevant_docs) > 0 else 0
    )
    summary = agent.summarise(url, retrieved_docs, contents)
    record["summary"] = summary
    record["gather_tokens"] = agent.tokens


def eval_class_build(
    categories_path: os.PathLike,
    repos: str,
    n_eval: int,
    repair_attempts: int,
    run_name: str,
    model: str = DEFAULT_MODEL,
    eval_only: List[str] = [],
):
    print(f"RUN NAME: {run_name}")
    print(f"EVALUATING WITH MODEL: {model}")
    test_cases = load_test_cases(repos)
    test_cases = list(filter(lambda x: x["test_type"] == "pytest", test_cases))
    test_cases = (
        list(filter(lambda x: any(e in x["url"] for e in eval_only), test_cases))
        if len(eval_only) > 0
        else test_cases
    )
    pprint(test_cases)
    records = []
    notify("starting eval")
    messages_dir = f"logs/messages/{run_name}"

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


def eval_build_project(
    agent: Agent,
    dockerfile,
    repo_name,
    record,
    url,
    repair_attempts,
    run_name,
    model_name,
    n,
):
    messages_dir = f"logs/messages/{run_name}"
    messages_fname = f"{model_name}-{repo_name}-build-{n}.json"
    print("eval build")
    n_tries = 0
    try:
        print("test_repair")
        agent = RepairAgent(
            agent.model, RepairAgent.init_system_message(url, dockerfile), verbose=False
        )
        # agent.verbose = True
        build_status, n_tries = agent.repair_dockerfile(
            url, dockerfile, repo_name, repair_attempts
        )
    except Exception as e:
        print(agent.messages)
        print(e)
        build_status = "failure"
        agent.save_messages(messages_fname, messages_dir)
        # raise e
    except KeyboardInterrupt:
        build_status = "failure"

    notify(f" - BUILD STATUS: {build_status.upper()} after {n_tries} repair attempt(s)")
    agent.save_messages(messages_fname, messages_dir)
    record[repo_name]["build_status"] = build_status
    record[repo_name]["n_tries"] = n_tries
