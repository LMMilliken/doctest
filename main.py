import argparse
import json
from pprint import pprint

from doc_test.agent import Agent, ClassAgent, GatherAgent, RepairAgent
from doc_test.consts import (
    CATEGORIES_PATH,
    DEFAULT_MODEL,
    FASTAPI,
    NO_SEARCH_SYSTEM_PROMPT_PATH,
    REPOS_5K_1K_PATH,
    REPOS_10K_5K_PATH,
    REPOS_20K_10K_PATH,
    REPOS_20K_GTE_PATH,
    REPOS_FASTAPI_PATH,
)
from doc_test.utils import generate_name
from eval import eval_class_build, eval_gather_build
from vm_control import VMController

REPO_SETS = {
    "20k+": REPOS_20K_GTE_PATH,
    "20k-10k": REPOS_20K_10K_PATH,
    "10k-5k": REPOS_10K_5K_PATH,
    "5k-1k": REPOS_5K_1K_PATH,
    "fastapi": REPOS_FASTAPI_PATH,
}


def classify_repo(repo_url: str, model, prev_messages) -> Agent:

    agent = ClassAgent(
        model=model,
        system=ClassAgent.init_system_message(
            repo_url, categories_path=CATEGORIES_PATH
        ),
        prev_messages=prev_messages,
    )
    agent.classify_repo(
        repo_url=repo_url,
        categories_path=CATEGORIES_PATH,
    )
    pprint(agent.targets)
    return agent


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

    repos = [REPO_SETS[eval_set] for eval_set in args.eval_set]
    if args.eval:
        if args.agent == "gather" or args.agent == "gather_PR":
            eval_gather_build(
                repo_sets=repos,
                n_eval=int(args.n_eval),
                repair_attempts=int(args.n_tries),
                model=args.model,
                run_name=run_name,
                eval_only=args.eval_only,
                perfect_recall=args.agent == "gather_PR",
            )
        else:
            eval_class_build(
                categories_path=CATEGORIES_PATH,
                repos=repos,
                n_eval=int(args.n_eval),
                repair_attempts=int(args.n_tries),
                model=args.model,
                run_name=run_name,
                eval_only=args.eval_only,
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
            if args.agent == "gather":
                agent = gather_repo(url, model=args.model, prev_messages=prev_messages)
            elif args.agent == "class":
                agent = classify_repo(
                    url, model=args.model, prev_messages=prev_messages
                )
                agent.gen_nl_description()
            else:
                agent = Agent(
                    model=args.model,
                    system=GatherAgent.init_system_message(
                        url, system_path=NO_SEARCH_SYSTEM_PROMPT_PATH
                    ),
                )
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
        help="whether to perform evaluation on the stored set of example repos.",
    )
    parser.add_argument(
        "--agent",
        default="gather",
        help=(
            "determines the type of agent to be used. "
            "Options are [gather, class, gather_PR]"
        ),
    )
    parser.add_argument(
        "--repo",
        default=FASTAPI,
        help="if not performing evaluation, specifies the repo to attempt to build.",
    )
    parser.add_argument(
        "--n_tries",
        default=2,
        help="Number of repair attempts to make before giving up.",
    )
    parser.add_argument(
        "--n_eval",
        default=3,
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
        "--eval_only",
        nargs="*",
        default=[],
        help=(
            "List of repo names, only these repos will be evaluated"
            "Separate names with a comma and no space"
        ),
    )
    parser.add_argument(
        "--eval_set",
        nargs="+",
        default=["10k-5k"],
        help=(
            "The set of repositories to perform evaluation on. "
            "Either 20k+, 10k-5k or 5k-1k."
        ),
    )
    parser.add_argument(
        "--prev_messages",
        nargs="*",
        help=(
            "path to a message log of a previous run, "
            "the agent will first replay these messages before actually querying the LLM."
        ),
        default=[
            "logs/messages/suffering-eevee/gpt-4o-mini-fastapi-gather-3.json",
            "logs/messages/suffering-eevee/gpt-4o-mini-fastapi-build-3.json",
        ],
    )
    args = parser.parse_args()
    run_name = generate_name()
    print(f"RUN:    {run_name}")
    try:
        main(args, run_name)
    except KeyboardInterrupt as e:
        pass
    finally:
        print("clearing cache...")
        VMController().clear_cache()
        print(f"FINISHED:   {run_name}")
