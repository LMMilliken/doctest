import argparse
import json
from doc_test.utils import wrap_message
from doc_test.consts import MODELS


def write_messages(run, repo, n):
    for model in MODELS:
        try:
            with open(f"logs/messages/{run}/{model}-{repo}-{n}.json", "r") as f:
                messages = json.load(f)
            break
        except:
            pass
    conversation = "\n\n".join([wrap_message(message) for message in messages])
    fname = f"logs/messages/{run}/{model}-{repo}-{n}.txt"
    with open(fname, "w") as f:
        f.write(conversation)
    print(fname)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run",
        help="path to the run to visualise",
        default="bounded-meditite",
    )
    parser.add_argument(
        "--repo", help="the name of the repo to inspect", default="fastapi"
    )
    parser.add_argument("-n", help="the round to inspect", default=None)
    args = parser.parse_args()
    if args.n is None:
        for i in range(10):
            try:
                write_messages(args.run, args.repo, i)
            except Exception as e:
                raise e
                break
    else:
        write_messages(args.run, args.repo, int(args.n))
