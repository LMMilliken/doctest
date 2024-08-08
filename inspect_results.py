import argparse
import json
import os
from pprint import pprint
from typing import Any, Dict, List, Union

import matplotlib.pyplot as plt

from doc_test.consts import MODELS

SUCCESS = "✅"
FAIL = "❌"
INSUFFICIENT = "➖"
MISSING = "❓"
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


def get_rows(repo_data: Dict[str, Dict[str, Any]], cols: List[str]):
    rows = [
        [repo_name] + [repo_dict[col] if col in repo_dict else MISSING for col in cols]
        for repo_name, repo_dict in repo_data.items()
    ]
    ret = [["repo"] + cols]
    ret.extend(rows)
    return ret


def get_data(runs) -> str:
    runs_dir = "logs/eval"
    contents = os.listdir(runs_dir)
    run_paths = []
    for run in runs:
        run_paths.extend([run_path for run_path in contents if run in run_path])
    print(run_paths)
    data = []
    for run_path in run_paths:
        with open(os.path.join(runs_dir, run_path), "r") as f:

            data.extend(json.load(f))

    repos = set(item for round in data for item in round.keys())
    pprint(repos)
    print(f"### {', '.join(runs)}:")
    repo_data = {repo: get_repo_data(data, repo) for repo in repos}
    rows = get_rows(
        repo_data,
        [
            "build_succ",
            "avg_tries",
            "avg_duration",
            "avg_retrieved",
            "avg_recall",
            "n_relevant",
            "build_status",
            "n_tries",
        ],
    )
    return rows


def get_repo_data(data: List[Dict[str, Any]], repo: str):
    build = [
        (
            FAIL
            if "build_status" not in rnd[repo]
            else status_dict[rnd[repo]["build_status"]]
        )
        for rnd in data
        if repo in rnd and "build_status" in rnd[repo]
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
    avg_tries = round(sum(avg_tries) / len(avg_tries), 3) if len(avg_tries) > 0 else -1
    durations = [
        rnd[repo]["duration"] if "duration" in rnd[repo] else 0
        for rnd in data
        if repo in rnd
    ]
    avg_durations = (
        round(sum(durations) / len(durations), 3) if len(durations) > 0 else -1
    )

    repo_data = {
        "build_status": "".join(build),
        "build_succ": build_succ,
        "n_tries": n_tries,
        "avg_tries": avg_tries,
        "avg_duration": avg_durations,
    }

    if any(["retrieved" in repo for repo in data[0].values()]):
        repo_data = table_gather(data, repo, repo_data)
    elif any(["categories" in repo for repo in data[0].values()]):
        repo_data = table_class(data, repo, repo_data)
    return repo_data


def table_gather(data, repo, repo_data):
    recall = [
        rnd[repo]["recall"] for rnd in data if repo in rnd and "recall" in rnd[repo]
    ]
    n_retrieved = [
        len(list(set(rnd[repo]["retrieved"]).intersection(set(rnd[repo]["relevant"]))))
        for rnd in data
        if repo in rnd and "retrieved" in rnd[repo]
    ]
    n_relevant = [
        len(rnd[repo]["relevant"])
        for rnd in data
        if repo in rnd and "relevant" in rnd[repo]
    ]
    if len(n_relevant) > 0:
        n_relevant = max(n_relevant)
    else:
        n_relevant = -1
    avg_recall = round(sum(recall) / len(recall), 3) if len(recall) > 0 else 0
    avg_retrieved = (
        round(sum(n_retrieved) / len(n_retrieved), 3) if len(recall) > 0 else 0
    )
    repo_data["recall"] = recall
    repo_data["n_relevant"] = n_relevant
    repo_data["avg_recall"] = avg_recall
    repo_data["avg_retrieved"] = avg_retrieved
    return repo_data
    data = [
        (
            "repo",
            "build_succ",
            "avg_tries",
            "avg_duration (s)",
            "avg_recall",
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
                avg_recall,
                n_relevant,
                build,
                n_tries,
            )
        )
    )
    return data
    print(array_to_markdown_table(data))


def table_class(data, repo, repo_data) -> str:
    repo_data["classification"] = "".join(
        [SUCCESS if rnd[repo]["correct"] else FAIL for rnd in data]
    )
    # data = [("repo", "classification status", "build status", "n_tries")]
    # data.extend(list(zip(repos, classification, build, n_tries)))
    return repo_data
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
    default=["formative-suicune"],
    help="path to the run to visualise",
)
args = parser.parse_args()
data = get_data(args.run)
print(array_to_markdown_table(data))
# recall = [row[5] for row in data[1:]]
# retrieved = [row[4] for row in data[1:]]
# build_rate = [int(row[1].split("/")[0]) / int(row[1].split("/")[1]) for row in data[1:]]
# scatter(recall, build_rate, "recall", "build_rate", "")
# scatter(retrieved, build_rate, "retrieved", "build_rate", "")
