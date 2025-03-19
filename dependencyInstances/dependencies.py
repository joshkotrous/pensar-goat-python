import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
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


# Function to validate URL for SSRF prevention
def is_safe_url(url):
    """Validate URL to prevent SSRF attacks."""
    if not url:
        return False
    
    # Only allow http and https URLs
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ['http', 'https']:
        return False
    
    # Extract hostname
    hostname = parsed_url.netloc.split(':')[0].lower()
    
    # Block requests to localhost and variants
    if hostname == 'localhost' or hostname.endswith('.localhost'):
        return False
    
    # Check if hostname is an IP address
    try:
        ip = ipaddress.ip_address(hostname)
        # Block private IP ranges, loopback, link-local, etc.
        if (
            ip.is_private or 
            ip.is_loopback or 
            ip.is_link_local or 
            ip.is_reserved or
            ip.is_multicast
        ):
            return False
    except ValueError:
        # Not an IP address
        pass
    
    # Allow the URL if it passes all checks
    return True

# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Protected against SSRF by validating URLs before making requests."""
    url = flask.request.args.get("url")
    
    if not is_safe_url(url):
        return "Error: URL validation failed for security reasons", 403
    
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error: Failed to fetch URL: {str(e)}", 500


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