import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import ipaddress
from urllib.parse import urlparse
from markupsafe import escape  # Import for XSS protection

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
    """Fixed SQL Injection"""
    username = flask.request.args.get("username")
    password = flask.request.args.get("password")

    # Use parameterized query with placeholders instead of string formatting
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
    return f"<h1>Welcome, {escape(user_input)}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Previously Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe yaml.safe_load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Vulnerable to XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# URL validation function to prevent SSRF
def is_safe_url(url):
    """
    Check if the URL is safe to request (not pointing to internal resources)
    """
    if not url or not isinstance(url, str):
        return False

    parsed_url = urlparse(url)
    
    # Check for http or https scheme
    if parsed_url.scheme not in ('http', 'https'):
        return False
    
    # Extract hostname
    hostname = parsed_url.netloc.split(':')[0]
    
    # Block localhost and variants
    if hostname in ('localhost', '127.0.0.1', '::1') or hostname.endswith('.local'):
        return False
    
    # Try to parse as IP address to check for private ranges
    try:
        ip = ipaddress.ip_address(hostname)
        
        # Block private, link-local and other special IPs
        if (ip.is_private or ip.is_loopback or ip.is_link_local or 
            ip.is_multicast or ip.is_reserved):
            return False
    except ValueError:
        # Not an IP address, hostname should be fine as long as it's not localhost
        pass
        
    return True


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Fixed SSRF vulnerability by validating URLs and disabling redirects"""
    url = flask.request.args.get("url")
    
    if not is_safe_url(url):
        return "Invalid URL or URL points to internal resources", 400
    
    try:
        # Disable redirects to prevent redirect-based SSRF
        response = requests.get(url, allow_redirects=False, timeout=10)
        
        # Check if the response is a redirect
        if response.status_code in (301, 302, 303, 307, 308):
            return "URL redirects are not allowed", 400
        
        return response.text
    except requests.RequestException:
        return "Error fetching URL", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Secure SSH connection with proper host key verification"""
    ssh = paramiko.SSHClient()
    
    # Load host keys from the system's known_hosts file
    ssh.load_system_host_keys()
    
    # Use RejectPolicy (default) to reject unknown hosts
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        # Connect to a trusted server
        ssh.connect("trusted-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        # Handle SSH exceptions properly
        return f"SSH connection error: {str(e)}"
    finally:
        ssh.close()


if __name__ == "__main__":
    app.run(debug=True)