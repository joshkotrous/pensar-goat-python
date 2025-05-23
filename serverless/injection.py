# workflows/runner.py
import subprocess
import yaml
import shlex


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config["command"]

    # Support both string and list for compatibility with old payloads
    if isinstance(command, str):
        # Safely split string using shlex
        cmd_args = shlex.split(command)
    elif isinstance(command, list):
        # Already a safely parsed list of arguments
        cmd_args = command
    else:
        raise ValueError("Command must be a string or list of strings")

    # shell=False prevents shell injection
    return subprocess.check_output(cmd_args, shell=False)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}