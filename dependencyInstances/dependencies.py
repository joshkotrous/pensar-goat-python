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
    """Vulnerable to XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=True)  # XXE enabled
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
def run_ssh_command(host, username, password, command="ls", known_hosts_file=None):
    """
    Execute a command on a remote server via SSH with proper host key verification.
    
    Args:
        host (str): The SSH server hostname or IP address
        username (str): SSH username
        password (str): SSH password
        command (str): Command to execute on the server
        known_hosts_file (str, optional): Path to known_hosts file for verification
        
    Returns:
        bytes: Output of the command
        
    Raises:
        paramiko.SSHException: If connection or authentication fails
        paramiko.BadHostKeyException: If host key verification fails
        ValueError: If required parameters are missing
    """
    if not host or not username or not password:
        raise ValueError("SSH host, username, and password are required")
    
    ssh = paramiko.SSHClient()
    
    # Load host keys for verification
    if known_hosts_file:
        ssh.load_host_keys(known_hosts_file)
    else:
        ssh.load_system_host_keys()
    
    # Reject unknown host keys instead of auto-accepting
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect(host, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.read()
    finally:
        ssh.close()


if __name__ == "__main__":
    app.run(debug=True)