# workflows/runner.py
import subprocess
import yaml
import shlex  # Pensar fix


def run_task_from_yaml(yaml_config):
    # Pensar fix: Safely parse the command and avoid shell=True
    config = yaml.safe_load(yaml_config)
    command = config["command"]

    if not isinstance(command, str):
        raise ValueError("Command must be a string.")  # Pensar fix

    # Safely split the command into arguments
    command_args = shlex.split(command)  # Pensar fix

    return subprocess.check_output(command_args)  # shell=False by default


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}