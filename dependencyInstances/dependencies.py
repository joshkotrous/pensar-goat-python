import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import ipaddress
from urllib.parse import urlparse
import os  # Added to access environment variables

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
    """Vulnerable to XSS"""
    user_input = flask.escape(flask.request.args.get("name", ""))
    return (
        f"<h1>Welcome, {user_input}!</h1>"  # Input is now sanitized to prevent XSS
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Load configuration from YAML file"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load to prevent arbitrary code execution
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Vulnerable to XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
def is_safe_url(url):
    """Check if a URL is safe to fetch (not pointing to internal resources)"""
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Ensure the scheme is http or https
    if parsed_url.scheme not in ('http', 'https'):
        return False
    
    # Check if hostname is provided
    if not parsed_url.netloc:
        return False
    
    # Check if it's an IP address
    hostname = parsed_url.netloc.split(':')[0]
    try:
        ip = ipaddress.ip_address(hostname)
        
        # Block private IP ranges
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast:
            return False
    except ValueError:
        # Not an IP address, check for localhost
        if hostname.lower() == 'localhost':
            return False
    
    return True

@app.route("/fetch")
def fetch():
    """Protected against credential leakage in redirects and SSRF"""
    url = flask.request.args.get("url")
    
    # Validate URL to prevent SSRF attacks
    if not url or not is_safe_url(url):
        return "Invalid or unsafe URL", 400
    
    # Limit redirects and set a timeout
    response = requests.get(url, allow_redirects=False, timeout=5)
    return response.text


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Secure SSH connection with proper host key validation"""
    ssh = paramiko.SSHClient()
    # Load system host keys instead of automatically accepting any key
    ssh.load_system_host_keys()
    # Set policy to reject unknown keys
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    try:
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.ssh_exception.SSHException as e:
        return f"SSH connection failed: {str(e)}"
    finally:
        ssh.close()


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)