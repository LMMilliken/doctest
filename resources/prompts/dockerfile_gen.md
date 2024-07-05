Now that you have gathered sufficient information about the repository, your new task is write a dockerfile to clone (<REPO_URL>) and then setup a working environment for the repository. To verify that any cloning and installation succeeds, `RUN` the repo's test suite at the end of the build process.
Here are some tips for successfully bulding a dockerfile:
- Once you clone the repository, make sure you are inside the repository directory before you proceed with installation.
- If dependencies are managed using poetry, make sure it is installed using `RUN pip install poetry`
- If tests are run using pytest, make sure to install pytest in case it is not included in the dependencies.
- make sure you use that the tests run during the build process, by using `RUN` when running tests. if the final line uses `CMD` then I will be eaten alive (bad). DO NOT EVER USE `CMD pytest`.
    - Dont add any additional arguments to pytest, that makes it harder for me to identify whether the build was successful.
    - Make sure your final line is `RUN pytest`.

use the `submit_dockerfile` function to provide the dockerfile.