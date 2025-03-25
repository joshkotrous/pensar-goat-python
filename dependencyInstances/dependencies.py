import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import urllib.parse  # For URL parsing
import re  # For regex pattern matching

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


# ======== 5. URL validation for SSRF prevention ========
def is_url_safe(url):
    """
    Validate URL to prevent SSRF attacks.
    Ensures the URL has an allowed scheme and doesn't point to internal networks.
    """
    try:
        parsed_url = urllib.parse.urlparse(url)
        
        # Check for allowed schemes
        if parsed_url.scheme not in ['http', 'https']:
            return False
        
        # Extract hostname (without port)
        hostname = parsed_url.hostname
        if not hostname:
            return False
        hostname = hostname.lower()
        
        # Block localhost variations
        if hostname in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
            return False
            
        # Block private IP ranges
        private_ip_patterns = [
            r'^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$',  # 10.0.0.0/8
            r'^172\.(1[6-9]|2[0-9]|3[0-1])\.\d{1,3}\.\d{1,3}$',  # 172.16.0.0/12
            r'^192\.168\.\d{1,3}\.\d{1,3}$',  # 192.168.0.0/16
            r'^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$',  # 127.0.0.0/8
            r'^169\.254\.\d{1,3}\.\d{1,3}$',  # 169.254.0.0/16
        ]
        
        # Check against IP patterns
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', hostname):
            for pattern in private_ip_patterns:
                if re.match(pattern, hostname):
                    return False
            
        return True
    except Exception:
        # If any parsing error occurs, consider the URL unsafe
        return False


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Fixed SSRF vulnerability with URL validation"""
    url = flask.request.args.get("url")
    
    # Validate URL to prevent SSRF
    if not url or not is_url_safe(url):
        return "Invalid or disallowed URL", 400
        
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