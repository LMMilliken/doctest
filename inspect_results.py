import argparse
import json
from pprint import pprint

from doc_test.consts import MODELS

SUCCESS = "✅"
FAIL = "✖"
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


def table(run, model) -> str:
    fname = f"logs/eval/{run}_{model}.json"
    with open(fname, "r") as f:
        data = json.load(f)
    print(f"### {run} - {model}:")

    repos = sorted(data[0].keys())
    classification = [
        "".join([SUCCESS if rnd[repo]["correct"] else FAIL for rnd in data])
        for repo in repos
    ]

    build = [
        "".join(
            [
                (
                    FAIL
                    if "build_status" not in rnd[repo]
                    else status_dict[rnd[repo]["build_status"]]
                )
                for rnd in data
            ]
        )
        for repo in repos
    ]
    build_succ = [
        f"{len([b for b in repo_built if b == SUCCESS])}/{sum([rnd[repo]['correct'] for rnd in data])}"
        for repo_built, repo in zip(build, repos)
    ]

    n_tries = [
        "".join(
            [
                (
                    FAIL
                    if "build_status" not in rnd[repo] or "n_tries" not in rnd[repo]
                    else str(rnd[repo]["n_tries"])
                )
                for rnd in data
            ]
        )
        for repo in repos
    ]
    avg_tries = [
        [rnd[repo]["n_tries"] + 1 for rnd in data if "n_tries" in rnd[repo]]
        for repo in repos
    ]
    avg_tries = [
        round(sum(repo) / len(repo), 3) if len(repo) > 0 else -1 for repo in avg_tries
    ]
    # data = [("repo", "classification status", "build status", "n_tries")]
    # data.extend(list(zip(repos, classification, build, n_tries)))
    durations = [
        [rnd[repo]["duration"] if "duration" in rnd[repo] else 0 for rnd in data]
        for repo in repos
    ]
    avg_durations = [round(sum(repo) / len(repo), 3) for repo in durations]
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


parser = argparse.ArgumentParser()
parser.add_argument(
    "--run",
    help="path to the run to visualise",
    default="bounded-meditite",
)
args = parser.parse_args()
for model in MODELS:
    try:
        table(args.run, model)
    except Exception as e:
        pass
