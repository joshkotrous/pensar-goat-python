import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks

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


# Helper function to validate URLs for SSRF prevention
def is_safe_url(url):
    """Check if a URL is safe to fetch (prevent SSRF)"""
    # Basic validation - ensure URL starts with http:// or https://
    if not url.startswith(('http://', 'https://')):
        return False
    
    # Extract the hostname
    try:
        hostname = url.split('://', 1)[1].split('/', 1)[0].split(':', 1)[0]
    except IndexError:
        return False
    
    # Check for unsafe hostnames
    unsafe_patterns = [
        'localhost', '127.', '0.0.0.0', 
        '10.', 
        '192.168.', 
        'internal', 'local', 'intranet'
    ]
    # Check for various 172.16-31 ranges (private IP addresses)
    for i in range(16, 32):
        unsafe_patterns.append(f'172.{i}.')
    
    hostname_lower = hostname.lower()
    for pattern in unsafe_patterns:
        if pattern in hostname_lower:
            return False
    
    return True


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Protected against SSRF"""
    url = flask.request.args.get("url")
    
    # Validate URL to prevent SSRF
    if not url:
        return "Missing URL parameter", 400
    
    if not is_safe_url(url):
        return "URL validation failed - possible SSRF attempt", 403
    
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