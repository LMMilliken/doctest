FUNC_INSPECT = {
    "type": "function",
    "function": {
        "name": "inspect",
        "description": ("retrieve the contents of a given directory, or file"),
        "parameters": {
            "type": "object",
            "properties": {
                "file_or_dir": {"type": "string", "enum": ["FILE", "DIRECTORY"]},
                "path": {
                    "type": "string",
                    "description": "path to the file or directory to be inspected",
                },
            },
            "required": ["file_or_dir", "path"],
        },
    },
}
FUNC_DIR = {
    "type": "function",
    "function": {
        "name": "get_directory_contents",
        "description": (
            "retrieve the contents of a given directory, "
            "including any files and subdirectories it contains."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "The path to the directory to be inspected",
                }
            },
            "required": ["directory"],
        },
    },
}

FUNC_FILE = {
    "type": "function",
    "function": {
        "name": "get_file_contents",
        "description": ("retrieve the headings of a given file."),
        "parameters": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "The path to the file to be inspected",
                }
            },
            "required": ["file"],
        },
    },
}
FUNC_HEADER = {
    "type": "function",
    "function": {
        "name": "inspect_header",
        "description": ("retrieve the contents of a given heading in a file."),
        "parameters": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "The path to the file to be inspected",
                },
                "heading": {
                    "type": "string",
                    "description": "The name of the section header to inspect",
                },
            },
            "required": ["file", "heading"],
        },
    },
}

FUNC_GUESS = {
    "type": "function",
    "function": {
        "name": "classify_repo",
        "description": (
            "classify repo into one of the possible categories "
            "based on its installation method."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Which method of installation is used out of:\n",
                    "enum": [],
                }
            },
            "required": ["category"],
        },
    },
}

FUNC_PRESENCE = {
    "type": "function",
    "function": {
        "name": "check_presence",
        "description": (
            "Confirm whether the given files exists in the project. "
            "Use this to confirm any assumptions you make, to preven hallucinations"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": "The path to the file",
                }
            },
            "required": ["file"],
        },
    },
}
FUNC_DOCKERFILE = {
    "type": "function",
    "function": {
        "name": "submit_dockerfile",
        "description": (
            "Given your current knowledge of the repo, provide a dockerfile to this "
            "function that clones the repo and sets up the repo, then runs tests"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "dockerfile": {
                    "type": "string",
                    "description": "The contents of the dockerfile",
                }
            },
            "required": ["dockerfile"],
        },
    },
}
FUNC_FIXABLE = {
    "type": "function",
    "function": {
        "name": "can_be_fixed",
        "description": (
            "Determine whether the given error is caused by a problem with "
            "the dockerfile, or some other cuase that you cannot fix."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "fixable": {
                    "type": "boolean",
                    "description": (
                        "Whether the dockerfile can be edited to avoid this "
                        "problem (True), or if there is an issue with the error (False)"
                    ),
                }
            },
            "required": ["fixable"],
        },
    },
}

FUNC_SUBMIT_FILE = {
    "type": "function",
    "function": {
        "name": "submit_documentation",
        "description": (
            "Submit and record the path to a file containing documentation"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "string",
                    "description": (
                        "Path to a file that contains documentation"
                        "relative to the root directory"
                    ),
                }
            },
            "required": ["file"],
        },
    },
}

FUNC_FINISHED = {
    "type": "function",
    "function": {
        "name": "finished_search",
        "description": (
            "Signal that you have found and submitted all documentation in the repo."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}
