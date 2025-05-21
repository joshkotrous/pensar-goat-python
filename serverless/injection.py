# workflows/runner.py
import subprocess
import yaml
import shlex


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config.get("command")

    # Input validation and parsing
    if command is None:
        raise ValueError("Missing 'command' key in YAML config.")

    if isinstance(command, str):
        command_args = shlex.split(command)
    elif isinstance(command, list) and all(isinstance(c, str) for c in command):
        command_args = command
    else:
        raise ValueError("'command' must be a string or a list of strings.")

    if not command_args:
        raise ValueError("'command' may not be empty.")

    return subprocess.check_output(command_args, shell=False)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}