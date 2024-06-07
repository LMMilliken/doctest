Attempting to build the project using this dockerfile is resulting in the following error:
```
<ERROR_LOG>
```
First, identify the cause of this error, then use the provided tool to return a fixed version of the dockerfile.
Some reminders:
 - Move into the cloned repo after you have cloned it.
 - correct installation should be verified using `RUN pytest -q --collect-only 2>&1 | head -n 3 | xargs pytest -sv`.
 - Makre sure any files you reference really do exist. Here are the contents of the repo's root directory:
<ROOT_DIRECTORY>