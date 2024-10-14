from typing import Any, Dict

FUNC_INSPECT_NAME = "inspect"
FUNC_INSPECT = {
    "type": "function",
    "function": {
        "name": FUNC_INSPECT_NAME,
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
FUNC_DIR_NAME = "get_directory_contents"
FUNC_DIR = {
    "type": "function",
    "function": {
        "name": FUNC_DIR_NAME,
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

FUNC_FILE_NAME = "get_file_contents"
FUNC_FILE = {
    "type": "function",
    "function": {
        "name": FUNC_FILE_NAME,
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
FUNC_HEADER_NAME = "inspect_header"
FUNC_HEADER = {
    "type": "function",
    "function": {
        "name": FUNC_HEADER_NAME,
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

FUNC_GUESS_NAME = "classify_repo"
FUNC_GUESS = {
    "type": "function",
    "function": {
        "name": FUNC_GUESS_NAME,
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

FUNC_PRESENCE_NAME = "check_presence"
FUNC_PRESENCE = {
    "type": "function",
    "function": {
        "name": FUNC_PRESENCE_NAME,
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
FUNC_DOCKERFILE_NAME = "submit_dockerfile"
FUNC_DOCKERFILE = {
    "type": "function",
    "function": {
        "name": FUNC_DOCKERFILE_NAME,
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
FUNC_FIXABLE_NAME = "can_be_fixed"
FUNC_FIXABLE = {
    "type": "function",
    "function": {
        "name": FUNC_FIXABLE_NAME,
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


FUNC_READY_TO_FIX_NAME = "finished_search"
FUNC_READY_TO_FIX = {
    "type": "function",
    "function": {
        "name": FUNC_READY_TO_FIX_NAME,
        "description": (
            "Signal that you have has gathered sufficient information"
            " and are ready to suggest a fix to the dockerfile."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

FUNC_SUBMIT_FILE_NAME = "submit_documentation"
FUNC_SUBMIT_FILE = {
    "type": "function",
    "function": {
        "name": FUNC_SUBMIT_FILE_NAME,
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

FUNC_FINISHED_NAME = "finished_search"
FUNC_FINISHED = {
    "type": "function",
    "function": {
        "name": FUNC_FINISHED_NAME,
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

FUNC_SUMMARISE_NAME = "submit_summary"
FUNC_SUMMARISE = {
    "type": "function",
    "function": {
        "name": FUNC_SUMMARISE_NAME,
        "description": "Submit a summary of the information you have gathered.",
        "parameters": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": (
                        "A summary of the information you have gathered in the previous step."
                    ),
                }
            },
            "required": ["summary"],
        },
    },
}

FUNC_DICT = {
    FUNC_FILE_NAME: FUNC_FILE,
    FUNC_FIXABLE_NAME: FUNC_FIXABLE,
    FUNC_INSPECT_NAME: FUNC_INSPECT,
    FUNC_DIR_NAME: FUNC_DIR,
    FUNC_HEADER_NAME: FUNC_HEADER,
    FUNC_GUESS_NAME: FUNC_GUESS,
    FUNC_PRESENCE_NAME: FUNC_PRESENCE,
    FUNC_DOCKERFILE_NAME: FUNC_DOCKERFILE,
    FUNC_SUBMIT_FILE_NAME: FUNC_SUBMIT_FILE,
    FUNC_FINISHED_NAME: FUNC_FINISHED,
    FUNC_SUMMARISE_NAME: FUNC_SUMMARISE,
}
