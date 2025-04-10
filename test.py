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
    """Fixed SQL Injection vulnerability using parameterized queries"""
    username = flask.request.args.get("username")
    password = flask.request.args.get("password")

    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
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
    """Fixed: Using yaml.safe_load to prevent Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using yaml.safe_load() instead of yaml.load()
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
def run_ssh_command(host, username, password, command, known_hosts_file=None):
    """
    Execute a command on an SSH server with proper security checks.
    
    Args:
        host (str): The hostname or IP address of the SSH server
        username (str): SSH username
        password (str): SSH password
        command (str): The command to execute
        known_hosts_file (str, optional): Path to known_hosts file. If None, system default is used.
        
    Returns:
        str: Command output
        
    Raises:
        paramiko.ssh_exception.SSHException: If there are SSH-related errors
        ValueError: If parameters are invalid
    """
    if not all([host, username, password, command]):
        raise ValueError("Missing required SSH parameters")
        
    ssh = paramiko.SSHClient()
    
    # Load system host keys
    ssh.load_system_host_keys(known_hosts_file)
    
    # Use RejectPolicy to reject unknown host keys by default
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        # Connect with timeout for safety
        ssh.connect(host, username=username, password=password, timeout=10)
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read()
        ssh.close()
        return output
    except Exception as e:
        ssh.close()
        raise e


if __name__ == "__main__":
    app.run(debug=True)