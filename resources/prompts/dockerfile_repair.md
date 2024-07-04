Now, suggest how to fix this error, then use the provided tool to return a fixed version of the dockerfile.
Some reminders:
- When cloning the repository, make sure to do it like so: `git clone <REPO_URL> .`
    - Including this period will clone the repo into the current directory, removing the need to change your working directory.
- Dont add any additional arguments to pytest, that makes it harder for me to identify whether the build was successful.
    - Make sure your final line is `RUN pytest`.
- Dont try to copy the requirements file from one place to another, that will lead to mistakes.
- Make sure any files you reference really do exist. Here are the contents of the repo's root directory:
<ROOT_DIRECTORY>
- It could be the case that additional requirements are needed to run tests, is there an additional requirements file?