import argparse
from doc_test.agent import GatherAgent, ClassAgent, RepairAgent, Agent
from doc_test.consts import (
    CATEGORIES_PATH,
    DEFAULT_MODEL,
    FASTAPI,
    NO_SEARCH_SYSTEM_PROMPT_PATH,
    REPOS_20K_GTE_PATH,
    REPOS_10K_5K_PATH,
    REPOS_5K_1K_PATH,
)
from doc_test.utils import generate_name
from vm_control import VMController
from eval.agent.eval import eval_class_build, eval_gather_build
from pprint import pprint


def classify_repo(repo_url: str, model) -> Agent:

    agent = ClassAgent(
        model=model,
        system=ClassAgent.init_system_message(
            repo_url, categories_path=CATEGORIES_PATH
        ),
    )
    agent.classify_repo(
        repo_url=repo_url,
        categories_path=CATEGORIES_PATH,
    )
    pprint(agent.targets)
    return agent


def gather_repo(repo_url: str, model) -> Agent:
    agent = GatherAgent(
        model=model,
        system=GatherAgent.init_system_message(repo_url),
        count_tokens=True,
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
    eval_only = args.eval_only.split(",") if args.eval_only is not None else []

    match args.eval_set:
        case "20k+":
            repos = REPOS_20K_GTE_PATH
        case "10k-5k":
            repos = REPOS_10K_5K_PATH
        case "5k-1k":
            repos = REPOS_5K_1K_PATH
        case _:
            print(f"invalid eval set: {args.eval_set}")
    if args.eval:
        if args.agent == "gather":
            eval_gather_build(
                repos=repos,
                n_eval=int(args.n_eval),
                repair_attempts=int(args.n_tries),
                model=args.model,
                run_name=run_name,
                eval_only=eval_only,
            )
        else:
            eval_class_build(
                categories_path=CATEGORIES_PATH,
                repos=repos,
                n_eval=int(args.n_eval),
                repair_attempts=int(args.n_tries),
                model=args.model,
                run_name=run_name,
                eval_only=eval_only,
            )

    else:
        if args.dockerfile is not None:
            with open(args.dockerfile, "r") as f:
                dockerfile = f.read()
        else:
            url = args.repo
            name = url.split("/")[-1][:-4]
            if args.agent == "gather":
                agent = gather_repo(url, model=args.model)
            elif args.agent == "class":
                agent = classify_repo(url, model=args.model)
                agent.gen_nl_description()
                dockerfile = agent.gen_dockerfile(url, name)
            else:
                agent = Agent(
                    model=args.model,
                    system=GatherAgent.init_system_message(
                        url, system_path=NO_SEARCH_SYSTEM_PROMPT_PATH
                    ),
                )
                dockerfile = agent.gen_dockerfile(url, name)
        agent = RepairAgent(
            args.model,
            RepairAgent.init_system_message(url, dockerfile),
            None,
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
            "Options are [gather, class, no_search]"
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
        help=(
            "List of repo names, only these repos will be evaluated"
            "Separate names with a comma and no space"
        ),
    )
    parser.add_argument(
        "--eval_set",
        default="10k-5k",
        help=(
            "The set of repositories to perform evaluation on. "
            "Either 20k+, 10k-5k or 5k-1k."
        ),
    )
    args = parser.parse_args()
    run_name = generate_name()
    print(f"RUN:    {run_name}")
    try:
        main(args, run_name)
    except Exception as e:
        raise e
    except KeyboardInterrupt as e:
        pass
    finally:
        print("clearing cache...")
        VMController().clear_cache()
        print(f"FINISHED:   {run_name}")
