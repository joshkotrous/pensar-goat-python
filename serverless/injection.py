# workflows/runner.py
import subprocess
import yaml


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config["command"]
    # Ensure command is a list of strings
    if not isinstance(command, list) or not all(isinstance(arg, str) for arg in command):
        raise ValueError("Invalid command format: command must be a list of strings")
    return subprocess.check_output(command, shell=False)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}