import argparse
import json
import os

from doc_test.utils import wrap_message


def write_messages(run, repo, n):
    messages_dir = f"logs/messages/{run}"
    contents = os.listdir(messages_dir)
    msg_paths = [path for path in contents if f"{repo}-gather-{n}.json" in path]

    if len(msg_paths) == 0:
        msg_paths = [path for path in contents if f"{repo}-{n}.json" in path]
        if len(msg_paths) == 0:
            return
        with open(os.path.join(messages_dir, msg_paths[0]), "r") as f:
            messages = json.load(f)

    else:
        build_paths = [path for path in contents if f"{repo}-build-{n}.json" in path]
        with open(os.path.join(messages_dir, msg_paths[0]), "r") as f:
            messages = json.load(f)
        if len(build_paths) > 0:
            with open(os.path.join(messages_dir, build_paths[0]), "r") as f:
                messages.extend(json.load(f))

    conversation = "\n\n".join([wrap_message(message) for message in messages])
    fname = os.path.join(messages_dir, msg_paths[0].replace(".json", ".txt"))
    with open(fname, "w") as f:
        f.write(conversation)
    print(fname)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run",
        help="path to the run to visualise",
        default="appropriated-pichu",
    )
    parser.add_argument(
        "--repo", help="the name of the repo to inspect", default="fastapi"
    )
    parser.add_argument("-n", help="the round to inspect", default=None)
    args = parser.parse_args()
    if args.n is None:
        for i in range(10):
            write_messages(args.run, args.repo, i)
    else:
        write_messages(args.run, args.repo, int(args.n))
