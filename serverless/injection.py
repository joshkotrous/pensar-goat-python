# workflows/runner.py
import subprocess
import yaml


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config.get("command")

    # Require command as a list of strings, not a string
    if (
        not isinstance(command, list) or
        not command or
        not all(isinstance(arg, str) for arg in command)
    ):
        raise ValueError("The 'command' field must be a non-empty list of strings.")

    # Run without shell, safely
    return subprocess.check_output(command, shell=False)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}