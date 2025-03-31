import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
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
    """Fixed SQL Injection vulnerability"""
    username = flask.request.args.get("username")
    password = flask.request.args.get("password")

    # Use parameterized query instead of string interpolation
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
    return (
        f"<h1>Welcome, {escape(user_input)}!</h1>"  # User input is now escaped to prevent XSS
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load instead of unsafe yaml.load()
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
@app.route("/fetch")
def fetch():
    """Fetch content from a URL with SSRF protection"""
    url = flask.request.args.get("url")
    
    # Basic validation - ensure URL is provided
    if not url:
        return "Error: No URL provided", 400
    
    # Parse the URL
    try:
        parsed_url = urlparse(url)
        
        # Ensure the URL has a scheme and netloc
        if not parsed_url.scheme or not parsed_url.netloc:
            return "Error: Invalid URL format", 400
            
        # Only allow HTTP and HTTPS schemes
        if parsed_url.scheme not in ['http', 'https']:
            return "Error: Only HTTP and HTTPS protocols are allowed", 400
        
        # Block private IP ranges and localhost
        hostname = parsed_url.netloc.split(':')[0]
        
        # Block localhost and variants
        if hostname in ['localhost', '127.0.0.1', '::1']:
            return "Error: Access to localhost is not allowed", 403
            
        # Block private IP ranges using regex patterns
        private_ip_patterns = [
            r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # 10.0.0.0/8
            r'^172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}',  # 172.16.0.0/12
            r'^192\.168\.\d{1,3}\.\d{1,3}',  # 192.168.0.0/16
            r'^169\.254\.\d{1,3}\.\d{1,3}',  # 169.254.0.0/16
            r'^127\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # 127.0.0.0/8
        ]
        
        for pattern in private_ip_patterns:
            if re.match(pattern, hostname):
                return "Error: Access to internal networks is not allowed", 403
            
    except Exception as e:
        return f"Error: Invalid URL - {str(e)}", 400
    
    # Now we can safely make the request
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.text
    except requests.RequestException as e:
        return f"Error making request: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Securely connects to an SSH server with proper key verification"""
    # Path to known_hosts file - can be a dedicated file rather than system default
    known_hosts_path = "known_hosts"
    
    ssh = paramiko.SSHClient()
    # Load the known hosts file if it exists
    try:
        ssh.load_host_keys(known_hosts_path)
    except FileNotFoundError:
        # First-time connection will need manual verification
        pass
    
    # Use RejectPolicy() instead of AutoAddPolicy() to prevent connecting to unknown hosts
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        # This will occur if the host's key is not in the known_hosts file
        return f"SSH connection failed: Host key verification failed. {str(e)}"


if __name__ == "__main__":
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True')