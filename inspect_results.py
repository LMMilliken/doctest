import json


with open("logs/eval.json", "r") as f:
    runs = json.load(f)

# for run in runs:
#     new_repos = {
#         r["name"]: {"correct": r["correct"], "nl_step": r["nl_step"]}
#         for r in run["repos"]
#     }
#     run["repos"] = new_repos

# with open("logs/eval2.json", "w") as f:
#     json.dump(runs, f)

commits = set([r["commit_id"] for r in runs])

commit_summary = {}
for c in commits:
    commit_runs = [r for r in runs if r["commit_id"] == c]
    total_score = sum([r["score"] for r in commit_runs])
    avg_score = total_score / len(commit_runs)
    repos = set([name for run in commit_runs for name in run["repos"].keys()])
    repo_scores = {
        r: float(
            len(
                [
                    c
                    for c in commit_runs
                    if r in [name for name in c["repos"].keys()]
                    and c["repos"][r]["correct"]
                ]
            )
        )
        / float(
            len([c for c in commit_runs if r in [name for name in c["repos"].keys()]])
        )
        for r in repos
    }
    commit_summary[c] = {"avg_score": avg_score, "repo_scores": repo_scores}
    if any(["categories" in repo for repo in commit_runs[0]["repos"].values()]):
        print()
        categories = set(
            [
                n
                for run in commit_runs
                for repo in run["repos"].values()
                for n in repo["categories"]
            ]
        )
        categories = set(
            [
                n
                for run in commit_runs
                for repo in run["repos"].values()
                for n in repo["categories"]
            ]
        )
        category_scores = {
            cat: float(
                len(
                    [
                        n
                        for run in commit_runs
                        for repo in run["repos"].values()
                        for n in repo["categories"]
                        if n == cat and repo["correct"]
                    ]
                )
            )
            / float(
                len(
                    [
                        n
                        for run in commit_runs
                        for repo in run["repos"].values()
                        for n in repo["categories"]
                        if n == cat
                    ]
                )
            )
            for cat in categories
        }
        commit_summary["category_scores"] = category_scores

with open("logs/summary.json", "w") as f:
    json.dump(commit_summary, f)
