import json
from pprint import pprint

SUCCESS = "✔"
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


def table(fname: str) -> str:
    with open(fname, "r") as f:
        data = json.load(f)

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

    data = [("repo", "classification status", "build status")]
    data.extend(list(zip(repos, classification, build)))

    print(array_to_markdown_table(data))


print("## GPT-3.5:")
table("logs/eval_3.5.json")

print("## GPT-4o")
table("logs/eval_gpt-4o.json")
