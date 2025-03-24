import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import urllib.parse
import ipaddress

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


# Function to validate URL safety
def is_safe_url(url):
    """Check if a URL is safe to make a request to (prevent SSRF)."""
    try:
        # Parse the URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Ensure scheme is http or https
        if parsed_url.scheme not in ['http', 'https']:
            return False
        
        # Extract hostname
        hostname = parsed_url.netloc.split(':')[0]
        
        # Check if hostname is an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            
            # Check if IP is private, loopback, or link-local
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
                
        except ValueError:
            # Hostname is not an IP address, it's a domain name
            # Prevent DNS rebinding by validating hostname format
            if not hostname or hostname.lower() in ['localhost', '127.0.0.1', '::1']:
                return False
        
        return True
    except Exception:
        # If any error occurs during validation, consider the URL unsafe
        return False


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Secured against SSRF attacks"""
    url = flask.request.args.get("url")
    
    if not url or not is_safe_url(url):
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