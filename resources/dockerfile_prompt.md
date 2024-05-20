Now that you have gathered sufficient information about the repository, your new task is write a dockerfile that will:
1. clone the repository, <REPO_URL>
2. install any necessary dependencies, as well as any needed for testing
3. Verify that installation was successfull by running tests (using `RUN`, not `CMD`)