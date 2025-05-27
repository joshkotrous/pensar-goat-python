# workflows/runner.py
import subprocess
import yaml


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    # Validate that 'command' exists and is a list of strings
    command = config.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(arg, str) for arg in command):
        raise ValueError("Invalid 'command': must be a non-empty list of strings, e.g., ['ls', '-l', '/']")

    # Execute command as argument list, not via shell
    return subprocess.check_output(command)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}