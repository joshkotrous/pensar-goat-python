# workflows/runner.py
import subprocess
import yaml
import shlex


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config["command"]

    # Ensure command is a list of arguments
    if isinstance(command, str):
        # Safely split the input string into arguments
        command_args = shlex.split(command)
    elif isinstance(command, list):
        command_args = [str(arg) for arg in command]
    else:
        raise ValueError("Invalid command format: must be string or list")

    return subprocess.check_output(command_args, shell=False)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}