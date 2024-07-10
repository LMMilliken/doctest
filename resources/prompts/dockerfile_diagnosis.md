Attempting to build the project using this dockerfile is resulting in the following error:
```
<ERROR_LOG>
```
Perform a diagnosis of this error. What do the error logs mean, and what could be causing the error?
Some reminders that might be helpful:
- Once you clone the repository, make sure you are inside the repository directory before you proceed with installation.
- Dont add any additional arguments to pytest, that makes it harder for me to identify whether the build was successful.
    - Make sure your final line is `RUN pytest`.
- Dont try to copy the requirements file from one place to another, that will lead to mistakes.
- Make sure any files you reference really do exist. Here are the contents of the repo's root directory:
<ROOT_DIRECTORY>
- It could be the case the repository has more than one requirements file, if (AND ONLY IF) you are certain the repository has multiple requirements files, it could be the case that the requirements from multiple files are needed to run tests.
- If you encounter an error that looks like the one shown below, it could be the case that you need to use a newer python version.
```
#9 11.05 ERROR: Cannot install <DEPENDENCY>==<VER_NUM> because these package versions have conflicting dependencies.
#9 11.05 
#9 11.05 The conflict is caused by:
#9 11.05     The user requested <DEPENDENCY>==<VER_NUM>
#9 11.05     The user requested (constraint) <DEPENDENCY>==<VER_NUM>
```