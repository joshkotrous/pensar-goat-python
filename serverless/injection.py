# workflows/runner.py
import subprocess
import yaml


def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config.get("command")
    # Validate: Command must be a non-empty list of non-empty strings
    if not isinstance(command, list) or not command or not all(isinstance(arg, str) and arg for arg in command):
        raise ValueError("Invalid command format: command must be a non-empty list of non-empty strings")
    # Remove shell=True so sequence is executed directly without shell, mitigating injection
    return subprocess.check_output(command)


# lambda_function.py
from workflows.runner import run_task_from_yaml


def handler(event, context):
    body = event.get("body", "{}")
    try:
        result = run_task_from_yaml(body)
        return {"body": result.decode()}
    except Exception as e:
        # Could log the error here if desired
        return {"body": f"Error executing command: {str(e)}"}