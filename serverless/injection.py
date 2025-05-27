# workflows/runner.py
import subprocess
import yaml


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config.get("command")
    if isinstance(command, list):
        if not command or not all(isinstance(x, str) for x in command):
            raise ValueError("The 'command' list must contain at least one string argument.")
        cmd_args = command
    elif isinstance(command, str):
        cmd_args = command.strip().split()
        if not cmd_args:
            raise ValueError("Command string is empty.")
    else:
        raise ValueError("The 'command' key must be a non-empty string or list of strings.")
    return subprocess.check_output(cmd_args)  # shell=False by default


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}