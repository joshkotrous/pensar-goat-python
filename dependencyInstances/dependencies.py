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


# ======== 5. Insecure Request Handling ========
def is_safe_url(url):
    """Validate if a URL is safe to request."""
    # List of allowed domains
    allowed_domains = ["example.com", "api.example.com", "trusted-site.org"]
    
    try:
        # Parse the URL to extract domain
        parsed_url = urlparse(url)
        
        # Check if schema and domain are valid
        if not parsed_url.scheme or not parsed_url.netloc:
            return False
            
        # Check if the domain is in our allowed list
        domain = parsed_url.netloc
        return any(domain.endswith(allowed) for allowed in allowed_domains)
    except Exception:
        # If URL parsing fails, consider it unsafe
        return False

@app.route("/fetch")
def fetch():
    """Protected against credential leakage in redirects"""
    url = flask.request.args.get("url")
    
    if not url:
        return "URL parameter is required", 400
    
    # Validate initial URL
    if not is_safe_url(url):
        return "URL not allowed", 403
    
    # Make request without following redirects
    response = requests.get(url, allow_redirects=False)
    
    # Handle redirects manually with validation
    max_redirects = 5
    redirect_count = 0
    
    # Check for redirect status codes (3xx)
    while 300 <= response.status_code < 400 and redirect_count < max_redirects:
        redirect_url = response.headers.get('Location')
        
        if not redirect_url:
            break
            
        # Validate redirect URL
        if not is_safe_url(redirect_url):
            return "Redirect URL not allowed", 403
        
        # Follow the redirect
        response = requests.get(redirect_url, allow_redirects=False)
        redirect_count += 1
    
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