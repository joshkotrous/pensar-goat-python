import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from urllib.parse import urlparse

app.config['SESSION_COOKIE_SECURE'] = True  # Required for Flask 1.0+ session handling

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
@app.route("/")

# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    """Vulnerable to XSS"""
    user_input = flask.request.args.get("name", "")
    return (
        f"<h1>Welcome, {user_input}!</h1>"  # No sanitization, allowing script injection
    )
# ======== 3. Arbitrary Code Execution via YAML ========

# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.load(file, Loader=yaml.Loader)  # Using unsafe yaml.load()
    return data
# ======== 4. External XML Entity (XXE) Attack ========

# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Vulnerable to XXE"""
    parser = ET.XMLParser(resolve_entities=False)  # Updated for compatibility with 4.6.5
    parser = ET.XMLParser(resolve_entities=True)  # XXE enabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)
# ======== 5. Insecure Request Handling ========

# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Vulnerable to credential leakage in redirects"""
    url = flask.request.args.get("url")
    response = requests.get(url, allow_redirects=True)
    return response.text
        "public-api.example.org"

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
    except Exception as e:

if __name__ == "__main__":
    app.run(debug=True)
    import os
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode)
        ssh.close()
        return result
    except paramiko.SSHException as e:
        print(f"SSH connection error: {e}")
        return b"SSH connection failed: Host key verification failed"


if __name__ == "__main__":
    app.run(debug=True)
    if not url or not is_url_allowed(url):
        return "Invalid or disallowed URL", 400
    
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        # Optionally validate the response content type before returning it
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' in content_type or 'application/json' in content_type:
            return response.text
        else:
            return "Unsupported content type", 400
    except Exception as e:
        # Avoid leaking error details that might reveal internal information
        return "Error fetching URL", 500


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
    ssh.connect("malicious-server.com", username="user", password="pass")
    stdin, stdout, stderr = ssh.exec_command("ls")
    return stdout.read()


if __name__ == "__main__":
    app.run(debug=True)