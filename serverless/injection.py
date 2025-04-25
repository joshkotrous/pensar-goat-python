# workflows/runner.py
import subprocess
import yaml
import shlex


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config["command"]

    # Support command as a list (recommended) or as a string
    if isinstance(command, str):
        args = shlex.split(command)
    elif isinstance(command, list):
        args = command
    else:
        raise ValueError("Invalid command type: must be string or list")

    return subprocess.check_output(args, shell=False)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}