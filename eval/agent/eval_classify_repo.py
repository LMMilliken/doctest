import os
import sys
import json
import pytest
from typing import Dict, List, Union
from doc_test.agent import OpenAIAgent
from doc_test.agent.agent import ToolUsingOpenAIAgent

sys.path.append(os.getcwd())


def load_test_cases(filename: str) -> List[Dict[str, Union[str, List[int]]]]:
    with open(filename, "r") as f:
        return json.load(f)


def eval_python(
    categories_path: str,
    followup_path: str,
    repos: str,
    model: str = "gpt-3.5-turbo-1106",
    use_tools: bool = False,
):
    test_cases = load_test_cases(repos)
    with open("resources/system.md", "r") as f:
        system = f.read()
    with open(categories_path, "r") as f:
        category_descriptions = json.load(f)
    score = 0
    for test in test_cases:
        url = test["url"]
        categories = test["categories"]
        print(f"REPO: {url}")
        if use_tools:
            agent = ToolUsingOpenAIAgent(
                model=model,
                system=OpenAIAgent.init_system_message(
                    url, categories_path=categories_path
                ),
                verbose=False,
            )
        else:
            agent = OpenAIAgent(
                model=model,
                system=OpenAIAgent.init_system_message(
                    url, categories_path=categories_path
                ),
                verbose=False,
            )
        try:
            prediction = agent.classify_repo(
                url,
                followup_path=followup_path,
                categories_path=categories_path,
            )
            print(f" - PREDICTION: {prediction} {category_descriptions[prediction-1]}")
        except Exception as e:
            print(e)
            prediction = "X"
        print(
            f" - {'O' if prediction in categories else 'X'} ({categories}: {category_descriptions[categories[0]-1]})"
        )
        print(f" - {agent.calls} calls")
        score += prediction in categories
    print(f"Evaluation complete, scored {score} / {len(test_cases)}")
