from doc_test.agent.utils import *
from doc_test.agent.functions import *
from doc_test.agent.functions import _get_file_contents

api_url = get_api_url("https://github.com/home-assistant/core.git")
readme = _get_file_contents(api_url, "README.rst")
headings = get_headings(readme)

print(headings)
