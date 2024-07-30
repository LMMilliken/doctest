Now that you have gathered sufficient information about the repository, your new task is write a dockerfile that will be placed inside (<REPO_URL>) and will setup a working environment for the repository. To verify that any cloning and installation succeeds, `RUN` the repo's test suite at the end of the build process.
Here are some tips for successfully writing a dockerfile:
- Since the dockerfile will be placed inside the repository, there is no need to clone the repo!
- To ensure that you dont miss any files important to installing the requirements, make sure to copy the *entirety* of the repo into the container. (`COPY . /app/`)
- If dependencies are managed using poetry, make sure it is installed using `RUN pip install poetry`
    - If this is the case, install dependencies using `poetry install --all-extras` to make sure you install everythig.
    - Furthermore, after installing the dependencies with poetry, make sure to preface every command with `RUN poetry run ...` to make sure it is being run in the right environment.
- If tests are run using pytest, make sure to install pytest in case it is not included in the dependencies. (`pip install pytest`)
- make sure that the tests run during the build process, by using `RUN` when running tests. If the final line uses `CMD` then I will be eaten alive (bad). DO NOT EVER USE `CMD <test command>`.
    - Dont add any additional arguments to the test command, that makes it harder for me to identify whether the build was successful.
    - Make sure your final line is `RUN <test command>`

use the `submit_dockerfile` function to provide the dockerfile.