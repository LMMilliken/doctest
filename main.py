import argparse
import json
import sys
from doc_test.agent.gather_agent import GatherAgent
from doc_test.agent.class_agent import ClassAgent
from doc_test.agent.repair_agent import RepairAgent
from doc_test.consts import (
    CATEGORIES_PATH,
    DEFAULT_MODEL,
    DOCKERFILE_REPAIR_SYSTEM_PROMPT_PATH,
    FASTAPI,
    REPOS_PATH,
)
from doc_test.utils import generate_name
from vm_control import VMController
from doc_test.agent import Agent
from doc_test.agent.agent import Agent
from eval.agent.eval import eval_class_build, eval_gather_build
from pprint import pprint


def classify_repo(repo_url: str, model: str = DEFAULT_MODEL) -> Agent:

    agent = ClassAgent(
        model=model,
        system=ClassAgent.init_system_message(
            repo_url, categories_path=CATEGORIES_PATH
        ),
    )
    category = agent.classify_repo(
        repo_url=repo_url,
        categories_path=CATEGORIES_PATH,
    )
    pprint(agent.targets)
    return agent


def main(args, run_name):
    url = args.repo
    repo_name = url.split("/")[-1][:-4]
    eval_only = args.eval_only.split(",") if args.eval_only is not None else []
    if args.eval:
        success = {}
        if args.gather:
            record = eval_gather_build(
                repos=REPOS_PATH,
                n_eval=int(args.n_eval),
                repair_attempts=int(args.n_tries),
                model=args.model,
                run_name=run_name,
                eval_only=eval_only,
            )
        else:
            record = eval_class_build(
                categories_path=CATEGORIES_PATH,
                repos=REPOS_PATH,
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
            if args.gather or True:
                agent = GatherAgent(
                    model=DEFAULT_MODEL,
                    system=GatherAgent.init_system_message(url),
                    count_tokens=True,
                )
                documents, contents = agent.gather(url)
                print("Gathered documents:")
                pprint(documents)
                response = agent.summarise(url, documents, contents)
                print(response)
                in_tokens = agent.in_tokens
                out_tokens = agent.out_tokens
                running_tokens = agent.running_tokens
                agent.save_messages("MESSAGES.json", ".")
                print(
                    (
                        f"IN_TOKENS: {in_tokens}\nOUT_TOKENS: {out_tokens}"
                        f"\nRUNNING_TOKENS: {running_tokens}"
                    )
                )
                return
            else:
                agent = classify_repo(url)
                agent.gen_nl_description()
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
        "--gather",
        action="store_true",
        help=(
            "If provided, the gathering agent will be used to gather the documentation "
            "found in the repo, instead of performing classification."
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
