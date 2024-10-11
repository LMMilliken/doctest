import json
import os
import time
from typing import Any, Dict, List, Optional

from doc_test.agent.gather_agent import GatherAgent
from doc_test.consts import (
    DEFAULT_MODEL,
    GATHER_SYSTEM_PERFECT_RECALL_PROMPT_PATH,
    REPO_SETS,
)
from doc_test.utils import notify
from eval.eval import (
    eval_build_project,
    eval_start,
    log_eval_end,
)


def eval_gather_build(
    repo_sets: List[str],
    n_eval: int,
    repair_attempts: int,
    run_name: str,
    model: str = DEFAULT_MODEL,
    eval_only: List[str] = [],
    perfect_recall: bool = False,
):
    test_cases, messages_dir = eval_start(repo_sets, run_name, model, eval_only)

    if perfect_recall:
        test_cases = list(
            filter(
                lambda x: "relevant_docs" in x and len(x["relevant_docs"]) > 0,
                test_cases,
            )
        )
        print(f"EVALUATING SUBSET OF TEST CASES WITH LENGTH {len(test_cases)}")
    records = []
    finished = False
    try:
        for i in range(n_eval):
            records.append({})
            record = records[-1]
            for test in test_cases:
                url = test["url"]
                ref = test.get("ref", None)
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
                        agent,
                        url,
                        test["relevant_docs"],
                        record[repo_name],
                        repo_name,
                        collected_docs=(
                            test["relevant_docs"] if perfect_recall else None
                        ),
                    )
                    dockerfile = agent.gen_dockerfile(url, repo_name)
                except Exception as e:
                    print(e)
                    continue
                finally:
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
                    i=i,
                    ref=ref,
                )

                duration = time.time() - start_time
                notify(f" - finished in {duration} seconds")
                record[repo_name]["duration"] = duration

            notify(f"EVAL ROUND {i} FIN:\n")

            with open(f"logs/eval/{run_name}_{model}.json", "w") as f:
                json.dump(records, f)
        finished = True
    finally:
        with open(f"logs/eval/{run_name}_{model}.json", "w") as f:
            json.dump(records, f)
        log_eval_end(finished)
    return records


def eval_gather_repo(
    agent: GatherAgent,
    url: str,
    relevant_docs: List[str],
    record: Dict[str, Any],
    repo_name: str,
    collected_docs: Optional[List[str]] = None,
    ref: Optional[str] = None,
):
    notify(f"REPO: {repo_name}")
    if collected_docs is None:
        retrieved_docs, contents = agent.gather(url, ref=ref)
    else:
        with open(GATHER_SYSTEM_PERFECT_RECALL_PROMPT_PATH, "r") as f:
            agent.system = f.read().replace("<REPO_NAME>", repo_name)
        retrieved_docs = collected_docs
        contents = {}
    notify(f" - COLLECTED DOCS: {retrieved_docs}")
    notify(f" - RELEVANT DOCS: {relevant_docs}")
    relevant_retrieved = set(retrieved_docs).intersection(set(relevant_docs))
    notify(f" - SCORE: {len(relevant_retrieved)}")
    record["retrieved"] = retrieved_docs
    record["relevant"] = relevant_docs
    record["recall"] = (
        len(relevant_retrieved) / len(relevant_docs) if len(relevant_docs) > 0 else 0
    )
    summary = agent.summarise(url, retrieved_docs, contents, ref=ref)
    record["summary"] = summary
    record["gather_tokens"] = agent.tokens
