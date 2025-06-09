# workflows/runner.py
import subprocess
import yaml
import shlex


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config.get("command")
    if isinstance(command, str):
        # Safely parse command string into list of args (avoids shell injection)
        args = shlex.split(command)
    elif isinstance(command, list):
        # Only allow command as list of strings
        args = command
    else:
        raise ValueError("Invalid 'command' format in YAML. Must be string or list.")
    if not args:
        raise ValueError("Command is empty.")
    return subprocess.check_output(args)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}