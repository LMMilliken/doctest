import argparse
import json
import os
from pprint import pprint
from typing import Any, Dict, List, Union

import matplotlib.pyplot as plt

from doc_test.consts import MODELS

SUCCESS = "✅"
FAIL = "❌"
INSUFFICIENT = "~"

status_dict = {"success": SUCCESS, "failure": FAIL, "insufficient": INSUFFICIENT}


def array_to_markdown_table(array):
    if not array or not array[0]:
        return ""

    header = array[0]
    rows = array[1:]

    # Create header row
    header_row = "| " + " | ".join(header) + " |"

    # Create separator row
    separator_row = "| " + " | ".join(["---"] * len(header)) + " |"

    # Create data rows
    data_rows = "\n".join("| " + " | ".join(map(str, row)) + " |" for row in rows)

    # Combine all parts
    markdown_table = "\n".join([header_row, separator_row, data_rows])

    return markdown_table


def table(runs) -> str:
    runs_dir = "logs/eval"
    contents = os.listdir(runs_dir)
    pprint(contents)
    run_paths = [
        run_path for run_path in contents if any([run in run_path for run in runs])
    ]
    print(run_paths)
    data = []
    for run_path in run_paths:
        with open(os.path.join(runs_dir, run_path), "r") as f:
            data.extend(json.load(f))
    repos = set(item for round in data for item in round.keys())
    pprint(repos)
    print(f"### {','.join(runs)}:")


def inspect_repo_data(data: List[Dict[str, Any]], repo: str):
    repo_data = {}

    build = [
        (
            FAIL
            if "build_status" not in rnd[repo]
            else status_dict[rnd[repo]["build_status"]]
        )
        for rnd in data
        if repo in rnd and "build_status" in [repo]
    ]

    build_succ = f"{len([b for b in build if b == SUCCESS])}/{len(build)}"

    n_tries = [
        (
            -1
            if "build_status" not in rnd[repo] or "n_tries" not in rnd[repo]
            else rnd[repo]["n_tries"]
        )
        for rnd in data
        if repo in rnd
    ]
    avg_tries = [
        rnd[repo]["n_tries"] + 1
        for rnd in data
        if repo in rnd and "n_tries" in rnd[repo]
    ]
    avg_tries = [
        round(sum(repo) / len(repo), 3) if len(repo) > 0 else -1 for repo in avg_tries
    ]
    durations = [
        rnd[repo]["duration"] if "duration" in rnd[repo] else 0
        for rnd in data
        if repo in rnd
    ]
    avg_durations = [round(sum(repo) / len(repo), 3) for repo in durations]

    repo_data = {
        "build": build,
        "build_succ": build_succ,
        "n_tries": n_tries,
        "avg_tries": avg_tries,
        "avg_durations": avg_durations,
    }

    if any(["retrieved" in repo for repo in data[0].values()]):
        data = table_gather(
            data, repo, build_succ, avg_tries, avg_durations, build, n_tries
        )
    elif any(["categories" in repo for repo in data[0].values()]):
        print("?>")
        data = table_class(
            data, repo, build_succ, avg_tries, avg_durations, build, n_tries
        )
    return data


def table_gather(data, repo, build_succ, avg_tries, avg_durations, build, n_tries):
    recall = [
        [rnd[repo]["recall"] for rnd in data if repo in rnd and "recall" in rnd[repo]]
        for repo in repos
    ]
    n_relevant = [len(data[0][repo]["relevant"]) for repo in repos]
    avg_retrieved = [
        round(sum(repo) / len(repo), 3) if len(repo) > 0 else 0 for repo in recall
    ]

    data = [
        (
            "repo",
            "build_succ",
            "avg_tries",
            "avg_duration (s)",
            "avg_retrieved",
            "n_relevant",
            "build status",
            "n_tries",
        )
    ]
    data.extend(
        list(
            zip(
                repos,
                build_succ,
                avg_tries,
                avg_durations,
                avg_retrieved,
                n_relevant,
                build,
                n_tries,
            )
        )
    )
    return data
    print(array_to_markdown_table(data))


def table_class(
    data, repos, build_succ, avg_tries, avg_durations, build, n_tries
) -> str:
    classification = [
        "".join([SUCCESS if rnd[repo]["correct"] else FAIL for rnd in data])
        for repo in repos
    ]
    # data = [("repo", "classification status", "build status", "n_tries")]
    # data.extend(list(zip(repos, classification, build, n_tries)))
    data = [
        (
            "repo",
            "build_succ",
            "avg_tries",
            "avg_duration (s)",
            "classification status",
            "build status",
            "n_tries",
        )
    ]
    data.extend(
        list(
            zip(
                repos,
                build_succ,
                avg_tries,
                avg_durations,
                classification,
                build,
                n_tries,
            )
        )
    )

    print(array_to_markdown_table(data))


def scatter(
    x_data: List[Union[int, float]],
    y_data: List[Union[int, float]],
    x_label: str = "x",
    y_label: str = "y",
    title: str = "title",
):
    plt.scatter(x_data, y_data)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.show()


parser = argparse.ArgumentParser()
parser.add_argument(
    "--run",
    nargs="+",
    default=["laughable-entei"],
    help="path to the run to visualise",
)
args = parser.parse_args()
print(args.run)
data = table(args.run)
recall = [row[4] for row in data[1:]]
build_rate = [int(row[1].split("/")[0]) / int(row[1].split("/")[1]) for row in data[1:]]
scatter(recall, build_rate, "recall", "build_rate", "")
print(array_to_markdown_table(data))
