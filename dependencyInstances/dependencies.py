import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
from flask import escape  # Import escape function for XSS protection
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import re
from urllib.parse import urlparse
import os  # Added for environment variable access

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

    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        return f"Welcome {user[1]}!"
    return "Invalid credentials."


# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    """Fixed XSS vulnerability"""
    user_input = flask.request.args.get("name", "")
    escaped_input = escape(user_input)  # Sanitize user input
    return f"<h1>Welcome, {escaped_input}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """No longer vulnerable to Arbitrary Code Execution"""
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


# Function to validate URLs for safety
def is_safe_url(url):
    """
    Validate that the URL is safe to access:
    1. Must have a valid URL scheme (http or https)
    2. Must not be an internal/private IP or localhost
    3. Must not have any authentication credentials in the URL
    """
    if not url:
        return False
        
    try:
        parsed_url = urlparse(url)
        
        # Check for valid scheme
        if parsed_url.scheme not in ['http', 'https']:
            return False
            
        # Check for authentication in URL
        if '@' in parsed_url.netloc:
            return False
        
        # Check for localhost or private IPs
        hostname = parsed_url.netloc.split(':')[0].lower()
        
        # Check for localhost
        if hostname == 'localhost' or hostname == '127.0.0.1' or hostname == '::1':
            return False
            
        # Check for private IPv4 ranges
        ipv4_pattern = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$')
        ipv4_match = ipv4_pattern.match(hostname)
        if ipv4_match:
            # Convert all parts to integers
            parts = [int(ipv4_match.group(i)) for i in range(1, 5)]
            
            # Check for private IP ranges
            if (parts[0] == 10 or  # 10.0.0.0/8
                (parts[0] == 172 and 16 <= parts[1] <= 31) or  # 172.16.0.0/12
                (parts[0] == 192 and parts[1] == 168)):  # 192.168.0.0/16
                return False
                
        return True
        
    except Exception:
        # If any error occurs during parsing, consider it unsafe
        return False


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Secured against open redirect vulnerabilities"""
    url = flask.request.args.get("url")
    
    if not is_safe_url(url):
        return "Invalid or potentially unsafe URL", 400
        
    try:
        response = requests.get(url, allow_redirects=True)
        return response.text
    except Exception as e:
        return f"Error fetching URL: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Secure SSH connection with proper host key verification"""
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()  # Load known host keys from system
    # Use RejectPolicy to reject connections to unknown servers
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect("trusted-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        return f"SSH connection failed: {str(e)}"
    finally:
        ssh.close()


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)