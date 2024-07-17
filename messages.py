import argparse
import json
from pprint import pprint

from doc_test.agent.agent import Agent
from doc_test.utils import wrap_message


parser = argparse.ArgumentParser()
parser.add_argument(
    "--run",
    help="path to the run to visualise",
    default="bounded-meditite",
)
parser.add_argument(
    "--model", help="name of the model used", default="gpt-3.5-turbo-1106"
)
parser.add_argument("--repo", help="the name of the repo to inspect", default="fastapi")
parser.add_argument("-n", help="the round to inspect", default=0)
args = parser.parse_args()

with open(
    f"logs/messages/{args.run}/{args.model}-{args.repo}-{int(args.n)}.json", "r"
) as f:
    messages = json.load(f)
conversation = "\n\n".join([wrap_message(message) for message in messages])
fname = f"logs/messages/{args.run}/{args.model}-{args.repo}-{int(args.n)}.txt"
with open(fname, "w") as f:
    f.write(conversation)
print(fname)
