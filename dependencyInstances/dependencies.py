import os
import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import re
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
    """Fixed SQL Injection vulnerability using parameterized queries"""
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
    """Protected against XSS"""
    user_input = flask.request.args.get("name", "")
    safe_input = flask.escape(user_input)  # Escape user input to prevent XSS
    return f"<h1>Welcome, {safe_input}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Protected against arbitrary code execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load instead of unsafe yaml.load()
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
@app.route("/fetch")
def fetch():
    """Protected against open redirect vulnerabilities"""
    url = flask.request.args.get("url")
    
    # Check if URL is None or empty
    if not url:
        return "No URL provided", 400
        
    # List of allowed domains
    allowed_domains = ['example.com', 'api.example.com', 'trusted-domain.com']
    
    # Parse the URL to extract the domain
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Check if the domain is in our allowed list
        if not domain or domain not in allowed_domains:
            return f"Domain '{domain}' is not allowed", 403
            
        # Make the request with a timeout to prevent long-running requests
        response = requests.get(url, allow_redirects=False)
        
        # Check if there's a redirect
        if response.is_redirect:
            return "Redirects are not allowed", 403
            
        return response.text
        
    except Exception as e:
        return f"Error processing URL: {str(e)}", 400


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Secure SSH connection with proper host key verification"""
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()  # Load known hosts from system
    
    # RejectPolicy will reject connections to unknown servers
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        result = stdout.read()
        ssh.close()
        return result
    except paramiko.SSHException as e:
        # Handle the case where the host key is not recognized
        return f"SSH Error: {str(e)}"


if __name__ == "__main__":
    # Default to False for security, can be overridden by environment variable
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)