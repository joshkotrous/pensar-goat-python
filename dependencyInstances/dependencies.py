import os
import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
from flask import escape  # Built-in Flask function, no new dependency
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
from urllib.parse import urlparse  # For URL validation

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
    """Fixed SQL Injection vulnerability"""
    username = flask.request.args.get("username")
    password = flask.request.args.get("password")

    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        return f"Welcome {user[1]}!"
    return "Invalid credentials."


# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    """Fixed XSS vulnerability by escaping user input"""
    user_input = flask.request.args.get("name", "")
    # Escape HTML special characters to prevent XSS
    escaped_input = escape(user_input)
    return f"<h1>Welcome, {escaped_input}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Formerly vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe yaml.safe_load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Fixed XXE vulnerability"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Protected against SSRF attacks with validation"""
    url = flask.request.args.get("url")
    
    # Validate URL
    try:
        parsed_url = urlparse(url)
        
        # Check for allowed schemes
        allowed_schemes = ['http', 'https']
        if parsed_url.scheme not in allowed_schemes:
            return "Invalid URL scheme. Only HTTP and HTTPS are allowed.", 400
        
        # Check for allowed hosts/domains
        allowed_domains = [
            'example.com', 
            'api.example.com',
            # Add other allowed domains here
        ]
        
        if parsed_url.netloc not in allowed_domains:
            return "Access to this domain is not allowed.", 403
        
        # Make the request with security settings
        response = requests.get(
            url, 
            allow_redirects=False,
            timeout=10,  # Set a timeout
            headers={'User-Agent': 'SecurityApp'}  # Set User-Agent
        )
        
        return response.text
    
    except Exception as e:
        return f"Error processing request: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Securely connects to SSH server with proper host key validation"""
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()  # Load keys from known_hosts file
    # Default policy is RejectPolicy if key is not in known_hosts
    try:
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        return f"SSH connection failed: {str(e)}"


if __name__ == "__main__":
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)