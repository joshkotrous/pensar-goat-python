import sqlite3
import yaml  # Vulnerable to arbitrary code execution
from flask import Flask, request  # Updated import style
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import os  # Added for environment variable access
app = Flask(__name__)
app = flask.Flask(__name__)

# ======== 1. SQL Injection Vulnerability ========
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
)
cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'password123')")
conn.commit()
conn.commit()

@app.route("/login")
def login():
    username = request.args.get("username")
    password = request.args.get("password")
    password = flask.request.args.get("password")

    query = (
        f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    )
    cursor.execute(query)
    user = cursor.fetchone()

    if user:
        return f"Welcome {user[1]}!"
    return "Invalid credentials."
    return "Invalid credentials."

# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    user_input = request.args.get("name", "")
    user_input = flask.request.args.get("name", "")
    return (
        f"<h1>Welcome, {user_input}!</h1>"  # No sanitization, allowing script injection
    )
    )

# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.load(file, Loader=yaml.Loader)  # Using unsafe yaml.load()
    return data
    return data

# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    xml_data = request.data
    parser = ET.XMLParser(resolve_entities=False)  # Updated for lxml 4.6.5+ compatibility
    parser = ET.XMLParser(resolve_entities=True)  # XXE enabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)
    return ET.tostring(tree)

# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    url = request.args.get("url")
    url = flask.request.args.get("url")
    response = requests.get(url, allow_redirects=True)
    return response.text
    # Validate URL to prevent SSRF

# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Vulnerable to RCE if connecting to an untrusted SSH server"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )  # Automatically accepting any key
    ssh.connect("malicious-server.com", username="user", password="pass")
    stdin, stdout, stderr = ssh.exec_command("ls")
    return stdout.read()
    try:

if __name__ == "__main__":
    # Use environment variable to control debug mode, default to False for safety
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)
    finally:
        ssh.close()


if __name__ == "__main__":
    app.run(debug=True)
            return False
        
        # Try to identify if it's an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            # Block private/internal IPs
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
        except ValueError:
            # Not an IP address, continue with other checks
            pass
            
        # Additional check for common internal domain patterns
        if hostname.endswith('.local') or hostname.endswith('.internal'):
            return False
            
        return True
    except Exception:
        return False


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Vulnerable to RCE if connecting to an untrusted SSH server"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )  # Automatically accepting any key
    ssh.connect("malicious-server.com", username="user", password="pass")
    stdin, stdout, stderr = ssh.exec_command("ls")
    return stdout.read()


if __name__ == "__main__":
    app.run(debug=True)