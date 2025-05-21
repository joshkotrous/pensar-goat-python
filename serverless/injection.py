# workflows/runner.py
import subprocess
import yaml
import shlex


def run_task_from_yaml(yaml_config):
    try:
        config = yaml.safe_load(yaml_config)
    except Exception as e:
        raise ValueError("Invalid YAML input") from e

    command = config.get("command")
    if not isinstance(command, str) or not command.strip():
        raise ValueError("Invalid or missing 'command' field in YAML")

    # Use shlex.split to safely tokenize the command string
    args = shlex.split(command)
    if not args:
        raise ValueError("Parsed command is empty")

    # Remove shell=True for security
    return subprocess.check_output(args)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    try:
        result = run_task_from_yaml(body)
        response = {"body": result.decode()}
    except Exception as e:
        response = {"body": f"Error: {str(e)}"}
    return response