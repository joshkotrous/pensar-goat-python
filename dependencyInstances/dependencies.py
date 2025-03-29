import os
import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import re
from urllib.parse import urlparse

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
    """Fixed SQL Injection vulnerability"""
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
    """Previously vulnerable to XSS, now fixed"""
    user_input = flask.request.args.get("name", "")
    safe_input = flask.escape(user_input)  # Sanitize user input to prevent XSS
    return f"<h1>Welcome, {safe_input}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Previously vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load instead of unsafe yaml.load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Protected against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


def is_safe_url(url):
    """Check if the URL is safe and not pointing to private/internal networks"""
    try:
        parsed_url = urlparse(url)
        
        # Check for proper scheme
        if parsed_url.scheme not in ['http', 'https']:
            return False
        
        hostname = parsed_url.netloc.split(':')[0].lower()
        
        # Check for localhost references
        if hostname in ['localhost', '127.0.0.1', '::1'] or hostname.startswith('127.'):
            return False
            
        # Check for private IP ranges
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', hostname):
            octets = hostname.split('.')
            if (octets[0] == '10' or  # 10.0.0.0/8
                (octets[0] == '172' and 16 <= int(octets[1]) <= 31) or  # 172.16.0.0/12
                (octets[0] == '192' and octets[1] == '168') or  # 192.168.0.0/16
                (octets[0] == '169' and octets[1] == '254')):  # 169.254.0.0/16
                return False
                
        return True
    except Exception:
        return False


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Fixed - Validates URL before making request"""
    url = flask.request.args.get("url")
    
    if not url:
        return "Error: URL parameter is required", 400
    
    # Validate the URL to prevent SSRF
    if not is_safe_url(url):
        return "Error: Invalid or unsafe URL provided", 403
    
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Securely connect to SSH server using known host keys"""
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()  # Load system host keys
    
    # Use RejectPolicy to reject unknown hosts
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect("server.example.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        return f"SSH connection error: {str(e)}"
    finally:
        ssh.close()


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)