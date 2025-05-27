# workflows/runner.py
import subprocess
import yaml
import shlex


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config["command"]
    if not isinstance(command, str) or not command.strip():
        raise ValueError("Invalid command input")
    args = shlex.split(command)
    return subprocess.check_output(args, shell=False)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}