import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
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
    """Protected against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# Function to validate URLs against allowlist
def is_url_allowed(url):
    """
    Validate URL against allowlist to prevent SSRF.
    Only allows specific schemes and hosts.
    """
    try:
        parsed_url = urlparse(url)
        
        # Define allowlisted schemes and hosts
        allowed_schemes = ['https', 'http']
        allowed_domains = ['api.example.com', 'public-api.example.org']
        
        # Check if scheme and host are allowed
        if parsed_url.scheme not in allowed_schemes:
            return False
        
        if parsed_url.netloc not in allowed_domains:
            return False
            
        # Prevent access to private networks
        if parsed_url.netloc.startswith('127.') or \
           parsed_url.netloc.startswith('localhost') or \
           parsed_url.netloc.startswith('10.') or \
           parsed_url.netloc.startswith('172.16.') or \
           parsed_url.netloc.startswith('172.17.') or \
           parsed_url.netloc.startswith('172.18.') or \
           parsed_url.netloc.startswith('172.19.') or \
           parsed_url.netloc.startswith('172.20.') or \
           parsed_url.netloc.startswith('172.21.') or \
           parsed_url.netloc.startswith('172.22.') or \
           parsed_url.netloc.startswith('172.23.') or \
           parsed_url.netloc.startswith('172.24.') or \
           parsed_url.netloc.startswith('172.25.') or \
           parsed_url.netloc.startswith('172.26.') or \
           parsed_url.netloc.startswith('172.27.') or \
           parsed_url.netloc.startswith('172.28.') or \
           parsed_url.netloc.startswith('172.29.') or \
           parsed_url.netloc.startswith('172.30.') or \
           parsed_url.netloc.startswith('172.31.') or \
           parsed_url.netloc.startswith('192.168.'):
            return False
            
        return True
    except Exception:
        # If URL parsing fails, consider it unsafe
        return False


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Protected against SSRF by validating URLs against an allowlist"""
    url = flask.request.args.get("url")
    
    # Validate URL against allowlist
    if not url or not is_url_allowed(url):
        return "Error: URL not allowed or invalid", 403
        
    # Add timeout to prevent long-running requests and disable redirects
    response = requests.get(url, allow_redirects=False, timeout=10)
    
    # Return response with an appropriate content type
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