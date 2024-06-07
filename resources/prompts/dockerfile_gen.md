Now that you have gathered sufficient information about the repository, your new task is write a dockerfile to clone (<REPO_URL>) and then setup a working environment for the repository. To verify that any cloning and installation succeeds, `RUN` the repo's test suite at the end of the build process.
Here are some tips for successfully bulding a dockerfile:
- After you clone the repository, remember to move into it!
- To reduce the amount of time spent testing, run tests like so:
    ```
    RUN pytest -q --collect-only 2>&1 | head -n 3 | xargs pytest -sv
    ```
    make sure you use `RUN`, if the final line uses `CMD` then I will be eaten alive (bad)