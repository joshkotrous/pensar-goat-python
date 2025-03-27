import sqlite3
import yaml  # Vulnerable to arbitrary code execution
from flask import Flask, request  # Updated import style
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import urllib.parse
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


@app.route("/login")
    username = request.args.get("username")
    password = request.args.get("password")
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
    user_input = request.args.get("name", "")
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
    xml_data = request.data
    parser = ET.XMLParser(resolve_entities=True, no_network=True)  # Updated parser config
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=True)  # XXE enabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
    url = request.args.get("url")
    """Protected against SSRF attacks"""
    url = flask.request.args.get("url")
    
    # Validate URL to prevent SSRF
    if not url:
        return "No URL provided", 400
    """Securely connect to an SSH server with proper host key verification"""
    # Basic URL validation
    ssh.load_system_host_keys()  # Load system host keys
    ssh.set_missing_host_key_policy(
        paramiko.RejectPolicy()
    )  # Reject unknown host keys
    try:
        ssh.connect("trusted-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(debug=debug_mode)


if __name__ == "__main__":
    app.run(debug=True)
    # Check against blocked hostnames
    if any(hostname == blocked or hostname.endswith('.' + blocked) or 
           hostname.startswith(blocked + '.') for blocked in blocked_hostnames):
        return "Access to internal resources is not allowed", 403
    
    # Check for private IP ranges
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_reserved:
            return "Access to internal networks is not allowed", 403
    except ValueError:
        # Not an IP address, continue with hostname checks
        pass
    
    try:
        # Limit redirects and set a timeout
        response = requests.get(
            url, 
            allow_redirects=False,  # Prevent redirect-based attacks
            timeout=5,              # Prevent long-running requests
            headers={               # Hide sensitive headers
                'User-Agent': 'Security-Hardened-App/1.0'
            }
        )
        
        # Only return responses from successful requests
        if response.status_code >= 300:
            return f"Request failed with status code: {response.status_code}", 400
            
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error retrieving URL: {str(e)}", 400


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