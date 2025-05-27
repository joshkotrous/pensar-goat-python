# workflows/runner.py
import subprocess
import yaml


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(item, str) for item in command):
        raise ValueError("The 'command' key must be a non-empty list of strings.")
    return subprocess.check_output(command, shell=False)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    try:
        result = run_task_from_yaml(body)
    except Exception as exc:
        # Return error message in body for API consumers.
        return {"body": str(exc)}
    return {"body": result.decode()}