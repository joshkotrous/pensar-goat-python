# workflows/runner.py
import subprocess
import yaml
import shlex


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config["command"]
    # Use shlex.split to safely parse the command string into a list
    command_args = shlex.split(command)
    # Pass the command as a list to subprocess.check_output without shell=True
    return subprocess.check_output(command_args)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}

