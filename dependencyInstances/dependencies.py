import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from urllib.parse import urlparse
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
    """Vulnerable to XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=True)  # XXE enabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
def is_url_safe(url):
    """Check if a URL is safe to access"""
    try:
        parsed_url = urlparse(url)
        
        # Ensure URL has a scheme and netloc
        if not parsed_url.scheme or not parsed_url.netloc:
            return False
        
        # Only allow http and https schemes
        if parsed_url.scheme not in ['http', 'https']:
            return False
        
        # Block access to private networks
        hostname = parsed_url.netloc.split(':')[0]
        if hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
            return False
            
        # Check for private IP ranges
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
        except ValueError:
            # Not an IP address, which is fine
            pass
            
        return True
    except Exception:
        return False

@app.route("/fetch")
def fetch():
    """Securely fetch content from external URLs"""
    url = flask.request.args.get("url")
    
    if not url:
        return "Missing URL parameter", 400
    
    if not is_url_safe(url):
        return "Invalid or disallowed URL", 403
    
    try:
        # Don't follow redirects automatically
        response = requests.get(url, allow_redirects=False, timeout=10)
        
        # Handle redirects manually with validation
        redirect_count = 0
        max_redirects = 5
        
        while (response.status_code in [301, 302, 303, 307, 308] and 
               redirect_count < max_redirects):
            redirect_url = response.headers.get('Location')
            
            # Validate the redirect URL
            if not is_url_safe(redirect_url):
                return "Redirect to disallowed URL", 403
                
            # Follow the redirect
            response = requests.get(redirect_url, allow_redirects=False, timeout=10)
            redirect_count += 1
            
        return response.text
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}", 500


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