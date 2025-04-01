import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import html  # Standard library for HTML escaping
import urllib.parse
import socket
import ipaddress
import os  # Added for environment variables

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
    """Protected against SQL Injection"""
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
    user_input = flask.request.args.get("name", "")
    return f"<h1>Welcome, {html.escape(user_input)}!</h1>"  # Sanitize user input to prevent XSS


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Fixed to prevent Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load() to prevent code execution
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Protected against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Securely fetches content from a URL with SSRF protection"""
    url = flask.request.args.get("url")
    
    # Basic validation: Check if URL is provided
    if not url:
        return "Error: URL parameter is required", 400
    
    # Parse the URL to validate it
    try:
        parsed_url = urllib.parse.urlparse(url)
        
        # Make sure the scheme is http or https
        if parsed_url.scheme not in ["http", "https"]:
            return "Error: Only HTTP and HTTPS protocols are allowed", 400
        
        # Resolve the hostname to an IP address
        hostname = parsed_url.netloc.split(':')[0]
        try:
            ip_address = socket.gethostbyname(hostname)
            
            # Check for private/internal IP addresses
            ip_obj = ipaddress.ip_address(ip_address)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                return "Error: Access to internal/private networks is forbidden", 403
                
        except socket.gaierror:
            return "Error: Cannot resolve hostname", 400
            
        # Make the request with proper protection
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.text
        
    except Exception as e:
        return f"Error: {str(e)}", 400


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Connects to SSH server with proper host key verification"""
    ssh = paramiko.SSHClient()
    # Load host keys from the system's known_hosts file
    ssh.load_system_host_keys()
    
    # Use RejectPolicy to refuse connections to unknown hosts
    # For production use with unknown hosts, first verify the host key fingerprint
    # and add it to known_hosts or implement a secure verification mechanism
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.ssh_exception.SSHException as e:
        return f"SSH connection error: {str(e)}"


if __name__ == "__main__":
    # Read debug mode from environment variable, default to False for security
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)