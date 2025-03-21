import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import re
import ipaddress
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
    """Protected against SSRF and credential leakage"""
    url = flask.request.args.get("url")
    
    # Input validation: check if URL is provided
    if not url:
        return "Error: No URL provided", 400
    
    # Validate URL format and restrict to HTTP/HTTPS
    if not re.match(r'^https?://', url):
        return "Error: Invalid URL scheme. Only HTTP/HTTPS allowed", 400
    
    # Block requests to private IP ranges, localhost and internal domains
    parsed_url = urlparse(url)
    hostname = parsed_url.hostname
    
    # Check if hostname is an IP address
    try:
        ip = ipaddress.ip_address(hostname)
        # Block private IP ranges
        if ip.is_private or ip.is_loopback or ip.is_multicast or ip.is_reserved:
            return "Error: Access to internal networks not allowed", 403
    except ValueError:
        # Not an IP address, check for localhost or other restricted domains
        if hostname.lower() == 'localhost' or hostname.endswith('.local') or hostname.endswith('.internal'):
            return "Error: Access to internal domains not allowed", 403
    
    try:
        # Disable redirects to prevent redirect-based attacks
        response = requests.get(url, allow_redirects=False, timeout=5)
        
        # Check if response is a redirect
        if response.status_code in (301, 302, 303, 307, 308):
            return "Redirects are not allowed", 403
        
        # Only return responses from successful requests
        if response.status_code != 200:
            return f"Error: Request failed with status code {response.status_code}", response.status_code
        
        # Filter the response to prevent sensitive data leakage
        content_type = response.headers.get('Content-Type', '')
        if not (content_type.startswith('text/html') or 
                content_type.startswith('text/plain') or
                content_type.startswith('application/json')):
            return "Error: Unsupported content type", 415
            
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error making request: {str(e)}", 500


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