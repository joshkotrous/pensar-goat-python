import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import os  # Added for environment variables

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

    # Use parameterized query instead of string interpolation
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    if user:
        return f"Welcome {user[1]}!"
    return "Invalid credentials."


# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    """Fixed XSS vulnerability"""
    user_input = flask.request.args.get("name", "")
    # Use flask.escape to prevent XSS attacks
    safe_input = flask.escape(user_input)
    return f"<h1>Welcome, {safe_input}!</h1>"


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Safe YAML loading"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load() to prevent code execution
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Protected against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE protection enabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
def is_safe_url(url):
    """Validate URL to prevent SSRF attacks."""
    try:
        from urllib.parse import urlparse
        import ipaddress
        
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            return False
            
        # Check hostname
        if not parsed.netloc:
            return False
            
        # Check if hostname is an IP address
        hostname = parsed.netloc.split(':')[0]
        try:
            ip = ipaddress.ip_address(hostname)
            
            # Block private, loopback, link-local addresses
            if (ip.is_private or ip.is_loopback or ip.is_link_local or 
                ip.is_multicast or ip.is_unspecified or ip.is_reserved):
                return False
                
        except ValueError:
            # Not an IP address, check for localhost
            if hostname.lower() == 'localhost':
                return False
                
        return True
    except Exception:
        return False

@app.route("/fetch")
def fetch():
    """Fetch content from a URL with SSRF protections"""
    url = flask.request.args.get("url")
    
    if not url or not is_safe_url(url):
        return "Invalid or potentially unsafe URL", 400
        
    try:
        response = requests.get(url, allow_redirects=True, timeout=10)
        return response.text
    except Exception as e:
        return f"Error fetching URL: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Execute an SSH command on a remote server with improved security"""
    try:
        ssh = paramiko.SSHClient()
        
        # Load system host keys instead of automatically accepting any key
        ssh.load_system_host_keys()
        
        # If the known host is not found, reject the connection
        # This replaces the dangerous AutoAddPolicy
        ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        
        # Use environment variables with secure defaults
        server = os.environ.get("SSH_SERVER", "localhost")
        username = os.environ.get("SSH_USERNAME", "admin")
        password = os.environ.get("SSH_PASSWORD", "")
        command = os.environ.get("SSH_COMMAND", "ls")
        
        # Prevent connection to known malicious servers
        if "malicious" in server.lower():
            return "Error: Connection to potentially malicious server blocked".encode()
        
        # Connect to the server with available credentials
        if password:
            ssh.connect(server, username=username, password=password)
        else:
            # Try to use the default key
            ssh.connect(server, username=username)
        
        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.read()
    except Exception as e:
        return f"Error: {str(e)}".encode()


if __name__ == "__main__":
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)