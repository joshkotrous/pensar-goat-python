# workflows/runner.py
import subprocess
import yaml
import shlex


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    if not isinstance(config, dict):
        raise ValueError("YAML config must be a mapping/object.")
    command = config.get("command")
    if not isinstance(command, str) or not command.strip():
        raise ValueError("The 'command' field must be a non-empty string.")
    # Safely split the command into arguments and execute without shell=True
    command_args = shlex.split(command)
    return subprocess.check_output(command_args)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}