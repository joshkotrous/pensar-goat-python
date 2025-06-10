# workflows/runner.py
import subprocess
import yaml


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config.get("command")
    if not isinstance(command, list) or not command:
        raise ValueError("The 'command' field must be a non-empty list of program arguments.")
    # Defensive: ensure every item is a string
    if not all(isinstance(arg, str) for arg in command):
        raise ValueError("All elements of the 'command' list must be strings.")
    return subprocess.check_output(command)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}