import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import os
import socket

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
def run_ssh_command(hostname, username, password, command="ls", port=22):
    """More secure SSH client with proper host key verification"""
    # Whitelist of trusted servers - add your known servers here
    TRUSTED_HOSTS = {
        "trusted-server.com",
        "localhost",
        "127.0.0.1",
    }
    
    # Input validation
    if not hostname or not username or not password or not command:
        return "Error: Missing required parameters"
    
    # Check against whitelist
    if hostname not in TRUSTED_HOSTS:
        return f"Error: Connection to {hostname} is not allowed"
    
    ssh = paramiko.SSHClient()
    
    try:
        # Load system host keys
        ssh.load_system_host_keys()
        
        # Use RejectPolicy by default (safer than AutoAddPolicy)
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        
        # Connect with timeout
        ssh.connect(hostname, port=port, username=username, password=password, timeout=10)
        
        # Execute command
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if error:
            return f"Error executing command: {error}"
        
        return output
    except paramiko.SSHException as e:
        return f"SSH Error: {str(e)}"
    except socket.error as e:
        return f"Connection Error: {str(e)}"
    except Exception as e:
        return f"Unexpected Error: {str(e)}"
    finally:
        ssh.close()


if __name__ == "__main__":
    app.run(debug=True)