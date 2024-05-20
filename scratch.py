from doc_test.agent.utils import *
from doc_test.agent.functions import *
from doc_test.agent.functions import _get_file_contents
from doc_test.vm_control import test_dockerfile

test_dockerfile("https://github.com/tiangolo/fastapi.git")


# print(headings)
