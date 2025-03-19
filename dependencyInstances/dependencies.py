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
    """
    Validate URLs against SSRF vulnerabilities
    - Checks for allowed schemes
    - Prevents access to private IP ranges and localhost
    """
    if not url:
        return False
    
    # List of allowed schemes
    ALLOWED_SCHEMES = {'http', 'https'}
    
    # Parse the URL
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ALLOWED_SCHEMES:
            return False
        
        # Block localhost and private IPs
        hostname = parsed.netloc.split(':')[0]
        if hostname in ('localhost', '127.0.0.1', '::1'):
            return False
        
        # Block private IPv4 ranges
        ip_pattern = re.compile(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$')
        ip_match = ip_pattern.match(hostname)
        if ip_match:
            octets = [int(octet) for octet in ip_match.groups()]
            # Check for private IP ranges:
            # 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
            if octets[0] == 10:
                return False
            if octets[0] == 172 and (16 <= octets[1] <= 31):
                return False
            if octets[0] == 192 and octets[1] == 168:
                return False
            # Check for link-local addresses (169.254.0.0/16)
            if octets[0] == 169 and octets[1] == 254:
                return False
        
        return True
    except Exception:
        return False


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Fixed SSRF vulnerability with URL validation"""
    url = flask.request.args.get("url")
    
    # Validate URL against SSRF
    if not is_safe_url(url):
        return "Invalid or disallowed URL", 400
    
    try:
        # Set strict parameters for request
        response = requests.get(
            url, 
            allow_redirects=False,  # Don't follow redirects for security
            timeout=10,             # Set timeout
            verify=True             # Verify SSL certificates
        )
        return response.text
    except requests.RequestException:
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