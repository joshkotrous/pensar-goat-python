# workflows/runner.py
import subprocess
import yaml


def run_task_from_yaml(yaml_config):
    # Pensar fix: Avoid shell=True and require command as a list to mitigate command injection
    config = yaml.safe_load(yaml_config)
    command = config.get("command")
    if not isinstance(command, list):
        raise ValueError("Invalid command: must be a list of arguments (Pensar fix)")
    return subprocess.check_output(command, shell=False)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}