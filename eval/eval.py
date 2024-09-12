import csv
import json
import os
import sys
import time
from datetime import date, datetime
from pprint import pprint
import traceback
from typing import Any, Dict, List, Optional, Union

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


def eval_start(
    repos: Union[os.PathLike, List[os.PathLike]], run_name, model, eval_only
):
    print(f"RUN NAME: {run_name}")
    print(f"EVALUATING WITH MODEL: {model}")
    if isinstance(repos, list):
        test_cases = []
        for repo_set in repos:
            test_cases.extend(load_test_cases(repo_set))
    else:
        test_cases = load_test_cases(repos)
    test_cases = (
        list(filter(lambda x: any(e in x["url"] for e in eval_only), test_cases))
        if len(eval_only) > 0
        else test_cases
    )
    pprint(test_cases)
    notify("starting eval")
    log_eval_start(
        run_name, model, repos if not isinstance(repos, list) else "-".join(repos)
    )
    messages_dir = f"logs/messages/{run_name}"
    return test_cases, messages_dir


def eval_build_project(
    agent: Agent,
    dockerfile,
    repo_name,
    record,
    url,
    repair_attempts,
    run_name,
    model_name,
    i,
    ref: Optional[str] = None,
):
    messages_dir = f"logs/messages/{run_name}"
    messages_fname = f"{model_name}-{repo_name}-build-{i}.json"
    print("eval build")
    n_tries = 0
    try:
        print("test_repair")
        agent = RepairAgent(
            agent.model, RepairAgent.init_system_message(url, dockerfile), verbose=False
        )
        # agent.verbose = True
        build_status, n_tries = agent.repair_dockerfile(
            url, dockerfile, repo_name, repair_attempts, ref=ref
        )
    except Exception as e:
        # record_error(e, repo_name, i)
        agent.messages.append(
            {
                "role": "error",
                "content": f"{str(type(e))[8:-2]}: {str(e)}\n{traceback.format_exc()}",
            }
        )
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


# def record_error(e: Exception, repo_name: str, i: int):
#     exception = {"message": str(e), "trace": traceback.format_exc()}
#     if repo_name in doc_test.err_log.errors:
#         doc_test.err_log.errors[repo_name][i] = exception
#     else:
#         doc_test.err_log.errors[repo_name] = {i: exception}