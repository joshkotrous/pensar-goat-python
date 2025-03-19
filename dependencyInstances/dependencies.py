import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import re
from urllib.parse import urlparse

app = flask.Flask(__name__)

# URL validation functions
def is_valid_url(url):
    """Check if URL is valid and has an allowed scheme."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
    except:
        return False

def is_safe_host(url):
    """Check that URL does not point to internal networks."""
    try:
        hostname = urlparse(url).netloc
        # Remove port if present
        if ':' in hostname:
            hostname = hostname.split(':')[0]
        
        # Check for localhost or private IPs
        if hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            return False
        
        # Check for private IP ranges
        ip_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        match = re.match(ip_pattern, hostname)
        if match:
            # Check for private IP ranges
            if match.group(1) == '10':  # 10.0.0.0/8
                return False
            if match.group(1) == '172' and 16 <= int(match.group(2)) <= 31:  # 172.16.0.0/12
                return False
            if match.group(1) == '192' and match.group(2) == '168':  # 192.168.0.0/16
                return False
            if match.group(1) == '169' and match.group(2) == '254':  # 169.254.0.0/16
                return False
        
        return True
    except:
        return False

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
    """Fixed insecure request handling vulnerability"""
    url = flask.request.args.get("url")
    
    # Validate URL before making request
    if not url or not is_valid_url(url) or not is_safe_host(url):
        return "Invalid or unsafe URL", 400
    
    response = requests.get(url, allow_redirects=True)
    return response.text


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