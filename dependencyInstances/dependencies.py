import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import urllib.parse
import ipaddress
import socket

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
    """Secure implementation against SSRF"""
    url = flask.request.args.get("url")
    if not url:
        return "URL parameter is required", 400
    
    try:
        # Parse and validate URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Validate scheme
        if parsed_url.scheme not in ['http', 'https']:
            return "URL scheme not allowed. Must be http or https", 403
        
        # Get hostname
        hostname = parsed_url.netloc.split(':')[0].lower()
        
        # Block localhost and common internal hostnames
        if hostname in ['localhost', '127.0.0.1', '::1', '0.0.0.0']:
            return "Access to internal hosts is forbidden", 403
        
        # Block private IP ranges by checking IP directly or resolving hostname
        try:
            # Try to parse as IP address
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_reserved:
                return "Access to internal IP addresses is forbidden", 403
        except ValueError:
            # Not an IP, try to resolve the hostname
            try:
                ip = ipaddress.ip_address(socket.gethostbyname(hostname))
                if ip.is_private or ip.is_loopback or ip.is_reserved:
                    return "Access to internal IP addresses is forbidden", 403
            except (socket.gaierror, ValueError):
                pass  # Continue if hostname can't be resolved
        
        # Make the request with a timeout
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.text
    except Exception as e:
        return f"Error processing request: {str(e)}", 400


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