import os

NL_STEP = True
DOCKERFILE_STEP = True

CATEGORIES_PATH = "resources/python_categories_limited.json"
REPOS_PATH = "eval/resources/python_repos_limited.json"

# prompts
PROMPTS_DIR = os.path.join("resources", "prompts")
## repo classification prompts
FOLLOWUP_PROMPT_PATH = os.path.join(PROMPTS_DIR, "classification_followup.md")
SYSTEM_PROMPT_PATH = os.path.join(PROMPTS_DIR, "system.md")
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
NL_PROMPT_PATH = os.path.join(PROMPTS_DIR, "installation_nl.md")

# misc
DEFAULT_REPAIR_TARGET = "eval/resources/dockerfiles/fastapi.dockerfile"
FASTAPI = "https://github.com/tiangolo/fastapi.git"
DEFAULT_MODEL = "gpt-3.5-turbo-1106"
