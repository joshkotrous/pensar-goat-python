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
    """Protected against SSRF by validating URLs"""
    url = flask.request.args.get("url")
    if not url:
        return "Error: No URL provided", 400
    
    try:
        # Parse the URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Validate scheme
        if parsed_url.scheme not in ['http', 'https']:
            return "Error: URL scheme not allowed", 403
        
        # Get the hostname
        hostname = parsed_url.netloc.split(':')[0]  # Remove port if present
        
        # Block localhost and common internal hostnames
        if hostname.lower() in ['localhost', 'internal', 'intranet', '127.0.0.1', '::1']:
            return "Error: URL not allowed", 403
            
        # Check if hostname is an IP
        try:
            ip_addr = ipaddress.ip_address(hostname)
            if ip_addr.is_loopback or ip_addr.is_private or ip_addr.is_reserved or ip_addr.is_multicast:
                return "Error: URL not allowed", 403
        except ValueError:
            # Not a direct IP address, try to resolve it
            try:
                ip = socket.gethostbyname(hostname)
                ip_addr = ipaddress.ip_address(ip)
                if ip_addr.is_loopback or ip_addr.is_private or ip_addr.is_reserved or ip_addr.is_multicast:
                    return "Error: URL not allowed", 403
            except (socket.gaierror, ValueError):
                # Cannot resolve hostname - could be legitimate or not
                # We'll continue and let the request library handle it
                pass
        
        # If all checks pass, proceed with the request
        response = requests.get(url, allow_redirects=True, timeout=10)  # Add timeout for safety
        return response.text
        
    except Exception:
        # Don't expose specific error details to the client
        return "Error: Could not fetch URL", 400


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