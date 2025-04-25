# workflows/runner.py
import subprocess
import yaml
import shlex

def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config.get("command")
    if isinstance(command, list):
        command_args = command
    elif isinstance(command, str):
        # Safely split the command string into arguments
        command_args = shlex.split(command)
    else:
        raise ValueError("Invalid 'command' type in YAML: must be string or list.")
    return subprocess.check_output(command_args)

# lambda_function.py
from workflows.runner import run_task_from_yaml

def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}