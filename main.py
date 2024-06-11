import argparse
import json
import sys
from doc_test.consts import (
    CATEGORIES_PATH,
    DEFAULT_MODEL,
    DOCKERFILE_STEP,
    FASTAPI,
    FOLLOWUP_PROMPT_PATH,
    NL_PROMPT_PATH,
    NL_STEP,
    REPOS_PATH,
)
from vm_control import VMController
from doc_test.agent import Agent
from doc_test.agent.agent import Agent
from eval.agent.eval import eval
from pprint import pprint


def classify_repo(repo_url: str, model: str = DEFAULT_MODEL) -> Agent:

    agent = Agent(
        model=model,
        system=Agent.init_system_message(repo_url, categories_path=CATEGORIES_PATH),
    )
    category = agent.classify_repo(
        repo_url=repo_url,
        followup_path=FOLLOWUP_PROMPT_PATH,
        categories_path=CATEGORIES_PATH,
    )
    pprint(agent.targets)
    return agent


def main(args):
    url = args.repo

    if args.eval:
        for i in range(1):
            eval(
                categories_path=CATEGORIES_PATH,
                followup_path=FOLLOWUP_PROMPT_PATH,
                repos=REPOS_PATH,
                dockerfile_step=DOCKERFILE_STEP,
                nl_step=NL_STEP,
            )
    else:
        with open("eval/resources/messages/proxy_pool.json", "r") as f:
            dockerfile = json.load(f)

        agent = Agent(DEFAULT_MODEL, None, dockerfile, verbose=True)

        if DOCKERFILE_STEP:
            # dockerfile = agent.gen_dockerfile(url=url)
            with open("eval/resources/dockerfiles/proxy_pool.dockerfile", "r") as f:
                dockerfile = f.read()
            success = agent.test_dockerfile(url, dockerfile)
            if not success:
                repo_name = url.split("/")[-1][:-4]
                agent.repair_dockerfile(
                    url=url, dockerfile=dockerfile, repo_name=repo_name
                )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--eval",
        action="store_true",
        help="whether to perform evaluation on the stored set of example repos.",
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
        "--from_messages",
        help=(
            "Path to a json file containing the logs from classification step. "
            "Providing this will skip classification and will attempt repair"
            "based on these messages. (--dockerfile must also be provided)"
        ),
    )
    parser.add_argument(
        "--dockerfile",
        help="Path to a dockerfile to be repaired.",
    )
    args = parser.parse_args()
    try:
        main(args)
    except Exception as e:
        raise e
    except KeyboardInterrupt as e:
        raise e
    finally:
        print("clearing cache...")
        VMController().clear_cache()
