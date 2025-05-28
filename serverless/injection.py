# workflows/runner.py
import subprocess
import yaml

# Allow-list of permitted commands and their allowed argument patterns.
# This must be defined and can be adjusted as per the application's needs.
# For example, only permit "echo" and "date" for illustration.
ALLOWED_COMMANDS = {
    "echo": None,  # None means any arguments permitted.
    "date": None,  # Add more allowed commands here as needed.
}

def validate_command(command):
    """
    Ensure 'command' is a list of non-empty strings and first element is in the allow-list.
    """
    if not isinstance(command, list):
        raise ValueError("Command must be a list of strings.")

    if len(command) == 0:
        raise ValueError("Command list is empty.")

    # Ensure all elements are non-empty strings
    if not all(isinstance(arg, str) and arg.strip() for arg in command):
        raise ValueError("All command arguments must be non-empty strings.")

    # Check the command name (first element) against the allow-list
    cmd_name = command[0]
    if cmd_name not in ALLOWED_COMMANDS:
        raise ValueError(f"Command '{cmd_name}' is not allowed.")

    # Additional argument validation can go here if specific patterns are required

    return command

def run_task_from_yaml(yaml_config):
    config = yaml.safe_load(yaml_config)
    command = config["command"]
    validated_command = validate_command(command)
    # Set a timeout (e.g., 10 seconds) to prevent resource abuse/DoS
    return subprocess.check_output(validated_command, shell=False, timeout=10)


# lambda_function.py
from workflows.runner import run_task_from_yaml

def handler(event, context):
    body = event.get("body", "{}")
    try:
        result = run_task_from_yaml(body)
        response_body = result.decode()
        status_code = 200
    except Exception as e:
        response_body = f"Error: {str(e)}"
        status_code = 400

    return {
        "statusCode": status_code,
        "body": response_body
    }