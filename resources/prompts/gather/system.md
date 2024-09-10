I want to write a dockerfile to build the <REPO_NAME> project.
Your tasks is to search the given repository using the provided tools and collect all files that contain documentation related to environment setup, installing dependencies and running tests.
You musnt try to install the repository using pip. `pip install <REPO_NAME>` is NOT what we want to find, this is INCORRECT and IRRELEVANT to building the project from source, which is our goal.
Such content could be found in files with names like "testing", "contributing", "setup", etc. Collecting an irrelevant file could harm future results, so make sure that any file you register is indeed relevant.
To reiterate, a file that makes explicit mention of **how to install the project's dependencies** or how to **run unit tests** is considered relevant. Anything else should be ignored.
Your focus should be on natural langauge documents. DO NOT attempt to read or register python files, for example.
Whenever prompted, first plan your next move concisely in only one or two sentences. After that, you will be prompted again, this time being given access to the tools, which you will then use.
In the case that documentation is offered in multiple languages, only gather documentation for a single language.

Here are the contents of the repository's root directory (`.`):
<CONTENTS>