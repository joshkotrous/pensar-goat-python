# workflows/runner.py
import subprocess
import yaml

# Define an allow-list of permitted commands
ALLOWED_COMMANDS = {"ls", "echo", "date"}  # Extend as appropriate

def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config.get("command")
    # Ensure command is a list, and first element is in the allowed commands
    if (
        not isinstance(command, list)
        or not command
        or command[0] not in ALLOWED_COMMANDS
    ):
        raise ValueError("Invalid or unauthorized command")
    # Run without shell=True, passing as argument list
    return subprocess.check_output(command, shell=False)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}