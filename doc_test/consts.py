import os

NL_STEP = True
DOCKERFILE_STEP = True

# model hparams
PER_MESSAGE_TOKEN_LIMIT = 10_000

CATEGORIES_PATH = "resources/python_categories_limited.json"
REPOS_PATH = "eval/resources/python_repos_limited.json"

# prompts
PROMPTS_DIR = os.path.join("resources", "prompts")
## repo classification prompts
CLASSIFICATION_FOLLOWUP_PROMPT_PATH = os.path.join(
    PROMPTS_DIR, "classification_followup.md"
)
CLASSIFICATION_SYSTEM_PROMPT_PATH = os.path.join(
    PROMPTS_DIR, "classification_system.md"
)
## summarization/dockerfile generation prompts
DOCKERFILE_PROMPT_PATH = os.path.join(PROMPTS_DIR, "dockerfile_gen.md")
DOCKERFILE_REPAIR_SYSTEM_PROMPT_PATH = os.path.join(
    PROMPTS_DIR, "dockerfile_repair_system.md"
)
DOCKERFILE_DIAGNOSIS_PROMPT_PATH = os.path.join(PROMPTS_DIR, "dockerfile_diagnosis.md")
DOCKERFILE_FAILURE_FOLLOWUP_PROMPT_PATH = os.path.join(
    PROMPTS_DIR, "dockerfile_failure_followup.md"
)
DOCKERFILE_FAILURE_PROMPT_PATH = os.path.join(PROMPTS_DIR, "dockerfile_failure.md")
DOCKERFILE_REPAIR_PROMPT_PATH = os.path.join(PROMPTS_DIR, "dockerfile_repair.md")
DOCKERFILE_REPAIR_HINTS_PATH = os.path.join(PROMPTS_DIR, "dockerfile_repair_hints.md")
NL_PROMPT_PATH = os.path.join(PROMPTS_DIR, "installation_nl.md")

# misc
DEFAULT_REPAIR_TARGET = "eval/resources/dockerfiles/fastapi.dockerfile"
FASTAPI = "https://github.com/tiangolo/fastapi.git"
DEFAULT_MODEL = "gpt-3.5-turbo-1106"
