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


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Safe handling of URL fetching with proper validation"""
    url = flask.request.args.get("url")
    
    # Validate URL
    if not url:
        return "Missing URL parameter", 400
    
    try:
        # 1. Validate URL scheme
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ['http', 'https']:
            return "Unsupported URL scheme. Only HTTP and HTTPS are allowed", 400
        
        # 2. Extract hostname without auth info
        netloc = parsed_url.netloc
        if '@' in netloc:
            netloc = netloc.split('@')[1]
        
        hostname = netloc.split(':')[0]  # Remove port if present
        
        # 3. Check for localhost variations
        if hostname.lower() == 'localhost' or hostname == '127.0.0.1' or hostname == '::1':
            return "Access to localhost not allowed", 403
            
        # 4. IP address check
        try:
            ip = ipaddress.ip_address(hostname)
            # Block private, loopback, link-local, and other non-routable IPs
            if not ip.is_global:
                return "Access to non-public networks not allowed", 403
        except ValueError:
            # Hostname is not an IP - this is fine
            pass
        
        # 5. Make the request with appropriate safeguards
        response = requests.get(
            url,
            allow_redirects=True,
            timeout=10,  # Prevent hanging connections
        )
        
        return response.text
        
    except Exception as e:
        return f"Error processing URL: {str(e)}", 400


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