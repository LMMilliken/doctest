import argparse
import json
from pprint import pprint

from doc_test.agent import Agent, GatherAgent, RepairAgent
from doc_test.consts import (
    DEFAULT_MODEL,
    FASTAPI,
    NO_SEARCH_SYSTEM_PROMPT_PATH,
)
from doc_test.utils import generate_name
from eval.eval_gather import eval_gather_build
from vm_control import VMController


def gather_repo(repo_url: str, model, prev_messages) -> Agent:
    agent = GatherAgent(
        model=model,
        system=GatherAgent.init_system_message(repo_url),
        count_tokens=True,
        prev_messages=prev_messages,
    )
    documents, contents = agent.gather(repo_url)
    print("Gathered documents:")
    pprint(documents)
    response = agent.summarise(repo_url, documents, contents)
    print(response)
    return agent


def main(args, run_name):
    url = args.repo
    repo_name = url.split("/")[-1][:-4]

    if args.eval:
        eval_gather_build(
            repo_sets=args.repo_sets,
            n_eval=int(args.n_eval),
            repair_attempts=int(args.n_tries),
            model=args.model,
            run_name=run_name,
            eval_only=args.eval_only,
            perfect_recall=args.PR == "gather_PR",
        )
    else:
        if args.dockerfile is not None:
            with open(args.dockerfile, "r") as f:
                dockerfile = f.read()
            prev_messages = []
        else:
            url = args.repo
            name = url.split("/")[-1][:-4]
            if args.prev_messages is not None:
                prev_messages = [json.load(open(p, "r")) for p in args.prev_messages]
                prev_messages = [msg for p in prev_messages for msg in p]
            agent = gather_repo(url, model=args.model, prev_messages=prev_messages)
            dockerfile = agent.gen_dockerfile(url, name)
            prev_messages = agent.prev_messages
        agent = RepairAgent(
            args.model,
            RepairAgent.init_system_message(url, dockerfile),
            None,
            prev_messages=prev_messages,
            verbose=True,
        )
        agent.repair_dockerfile(
            url=url,
            dockerfile=dockerfile,
            repo_name=repo_name,
            n_tries=int(args.n_tries),
        )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--eval",
        action="store_true",
        help=(
            "whether to perform evaluation on the stored set of example repos. "
            "If not set, only a single repo (--repo) will be targeted"
        ),
    )
    parser.add_argument(
        "--repo",
        default=FASTAPI,
        help="Specifies the target repository if only attempting to build a single repo.",
    )
    parser.add_argument(
        "--PR",
        action="store_true",
        help=(
            "If set, skips the documentation gathering step and "
            "provides the agent with all relevant documents."
        ),
    )
    parser.add_argument(
        "--n_tries",
        default=2,
        help="Number of repair attempts to make before giving up.",
    )
    parser.add_argument(
        "--n_eval",
        default=10,
        help="Number of times to repeat evaluation.",
    )
    parser.add_argument(
        "--model",
        help="name of the openai model to use as the agent.",
        default=DEFAULT_MODEL,
    )
    parser.add_argument(
        "--dockerfile",
        help="Path to a dockerfile to be repaired.",
    )
    parser.add_argument(
        "--repo_sets",
        nargs="+",
        default=["5-10k"],
        help=(
            "The set of repositories to perform evaluation on, "
            "either 20k+, 10-20k, 5-10k or 1-5k."
        ),
    )
    parser.add_argument(
        "--prev_messages",
        nargs="*",
        help=(
            "path to message log(s) of a previous run, "
            "the agent will first replay these messages before actually querying the LLM."
        ),
    )
    args = parser.parse_args()
    run_name = generate_name()
    print(f"RUN:    {run_name}")
    print(args.PR)
    try:
        main(args, run_name)
    except KeyboardInterrupt as e:
        pass
    finally:
        print("clearing cache...")
        VMController().clear_cache()
        print(f"FINISHED:   {run_name}")
