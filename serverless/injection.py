# workflows/runner.py
import subprocess
import yaml
import shlex


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config["command"]
    # Allow command as list or string, but prohibit shell metacharacters and shell=True
    if isinstance(command, list):
        cmd_args = command
    elif isinstance(command, str):
        cmd_args = shlex.split(command)
    else:
        raise ValueError("Invalid command format: must be a list or string")
    # Additional minimal check: prohibit empty command
    if not cmd_args or not isinstance(cmd_args[0], str):
        raise ValueError("Command must not be empty and must start with a string")
    return subprocess.check_output(cmd_args, shell=False)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    result = run_task_from_yaml(body)
    return {"body": result.decode()}