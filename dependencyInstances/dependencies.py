import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks

app = flask.Flask(__name__)

# ======== 1. SQL Injection Vulnerability ========
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
)
cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'password123')")
conn.commit()


@app.route("/login")
def login():
    """Vulnerable to SQL Injection"""
    username = flask.request.args.get("username")
    password = flask.request.args.get("password")

    query = (
        f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    )
    cursor.execute(query)
    user = cursor.fetchone()

    if user:
        return f"Welcome {user[1]}!"
    return "Invalid credentials."


# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    """Vulnerable to XSS"""
    user_input = flask.request.args.get("name", "")
    return (
        f"<h1>Welcome, {user_input}!</h1>"  # No sanitization, allowing script injection
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.load(file, Loader=yaml.Loader)  # Using unsafe yaml.load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Protected against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Vulnerable to credential leakage in redirects"""
    url = flask.request.args.get("url")
    response = requests.get(url, allow_redirects=True)
    return response.text


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command(hostname, username, password, command):
    """Execute a command over SSH with proper security controls
    
    Args:
        hostname: The hostname to connect to
        username: The SSH username
        password: The SSH password
        command: The command to execute
        
    Returns:
        The command output
        
    Raises:
        ValueError: If hostname or command is not allowed
        paramiko.ssh_exception.SSHException: On SSH connection issues
    """
    # Validate the hostname against a whitelist
    allowed_hosts = ["trusted-server1.com", "trusted-server2.com"]
    if hostname not in allowed_hosts:
        raise ValueError(f"Cannot connect to untrusted host: {hostname}")
    
    # Validate the command against a whitelist or for dangerous patterns
    dangerous_patterns = [";", "&&", "||", "`", "$", ">", "<", "|", "rm", "mkfs", "dd"]
    if any(pattern in command for pattern in dangerous_patterns):
        raise ValueError(f"Command contains dangerous pattern: {command}")
    
    # Only allow certain commands
    allowed_commands = ["ls", "pwd", "whoami", "date"]
    command_base = command.split()[0] if command else ""
    if command_base not in allowed_commands:
        raise ValueError(f"Command not in whitelist: {command}")
    
    # Use SSH with proper key verification
    ssh = paramiko.SSHClient()
    # Load known_hosts file
    ssh.load_system_host_keys()
    # Use RejectPolicy instead of AutoAddPolicy
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect(hostname, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.read()
    finally:
        ssh.close()


if __name__ == "__main__":
    app.run(debug=True)