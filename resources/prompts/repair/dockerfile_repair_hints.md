- If you are testing with pytest, make sure the final line is `RUN pytest`
    - If you are using poetry, then `RUN poetry run pytest`.
- If you are testing with make, the correct command is likely `make test`, not `make tests`.
- trying to copy the requirements file from one place to another will often lead to mistakes. Avoid this too
- Make sure any files that are referenced really do exist. Here are the contents of the repo's root directory, `.` (not including the dockerfile, which you have already been shown):
<ROOT_DIRECTORY>
- It could be the case the repository has more than one requirements file, if (AND ONLY IF) you are certain the repository has multiple requirements files, it could be the case that the requirements from multiple files are needed to run tests.
- If you encounter an error like this: `ERROR: Cannot find command 'git' - do you have 'git' installed and in your PATH?`, then you need to install git like so: `apt install git`
- If you encounter an error that looks like the one shown below, it could be the case that you need to use a newer python version.
```
#9 11.05 ERROR: Cannot install <DEPENDENCY>==<VER_NUM> because these package versions have conflicting dependencies.
#9 11.05 
#9 11.05 The conflict is caused by:
#9 11.05     The user requested <DEPENDENCY>==<VER_NUM>
#9 11.05     The user requested (constraint) <DEPENDENCY>==<VER_NUM>
```
- If you encounter an error such as No module named '<PROJECT_NAME>.xxx' , where the name of the  missing module is also the name of the project you are setting up, then you may need to compile the project before testing.
    - You can do this after installing the requirements like so: `pip install wheel ; pip install --no-build-isolation --editable .`