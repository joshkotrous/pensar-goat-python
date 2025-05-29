# workflows/runner.py
import subprocess
import yaml
import shlex


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config.get("command")
    if isinstance(command, str):
        # Safely split to list of arguments
        args = shlex.split(command)
    elif isinstance(command, list):
        # Ensure all elements are strings
        if not all(isinstance(arg, str) for arg in command):
            raise ValueError("All command arguments must be strings")
        args = command
    else:
        raise ValueError("Command must be a string or list of strings")
    return subprocess.check_output(args, shell=False)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}