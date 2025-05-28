# workflows/runner.py
import subprocess
import yaml


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config.get("command")

    # Validate that the command is a non-empty list of strings
    if (not isinstance(command, list) or
        not command or
        not all(isinstance(arg, str) for arg in command)):
        raise ValueError("Command must be a non-empty list of strings.")

    return subprocess.check_output(command)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}