# workflows/runner.py
import subprocess
import yaml


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config.get("command")
    if not command:
        raise ValueError("Command not specified in YAML config")

    # Accept either a string or a list; convert string to list for safety
    if isinstance(command, str):
        # Split the string into arguments (simple space split for compatibility; more advanced splitting could be implemented with shlex, but not introducing dependency)
        command_args = command.strip().split()
        if not command_args:
            raise ValueError("Command string is empty")
    elif isinstance(command, list):
        command_args = [str(arg) for arg in command]
        if not command_args:
            raise ValueError("Command list is empty")
    else:
        raise ValueError("Command must be a string or list of arguments")
    return subprocess.check_output(command_args, shell=False)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}