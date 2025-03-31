import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import urllib.parse
import ipaddress
import os  # Added to access environment variables

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
    """Protected against SQL Injection"""
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
    """Vulnerable to XSS"""
    user_input = flask.request.args.get("name", "")
    return f"<h1>Welcome, {flask.escape(user_input)}!</h1>"  # Sanitize user input
    

# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe yaml.load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Previously vulnerable to XXE, now fixed"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
def is_valid_url(url):
    """Check if a URL is valid and doesn't point to internal resources"""
    if not url or not isinstance(url, str):
        return False
        
    # Check for allowed schemes
    if not url.startswith(('http://', 'https://')):
        return False
    
    try:
        parsed_url = urllib.parse.urlparse(url)
        hostname = parsed_url.netloc
        
        # Strip port if present
        if ':' in hostname:
            hostname = hostname.split(':')[0]
        
        # Check for localhost variations
        if hostname in ['localhost', '127.0.0.1', '::1']:
            return False
            
        # Try to check if it's an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            # Block private IPs
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                return False
        except ValueError:
            # Not an IP address, this is fine
            pass
                
        return True
    except:
        return False

@app.route("/fetch")
def fetch():
    """Protected against SSRF attacks"""
    url = flask.request.args.get("url")
    
    if not is_valid_url(url):
        return "Invalid or disallowed URL", 400
        
    try:
        # Make the request with safety measures
        response = requests.get(
            url, 
            allow_redirects=False,  # Prevent redirects
            timeout=10,             # Set timeout
            verify=True             # Verify SSL certificates
        )
        return response.text
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {str(e)}", 500


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Securely connects to SSH server with proper host key verification"""
    ssh = paramiko.SSHClient()
    
    # Load system host keys
    ssh.load_system_host_keys()
    
    # Use RejectPolicy instead of AutoAddPolicy to prevent MITM attacks
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect("malicious-server.com", username="user", password="pass")
        stdin, stdout, stderr = ssh.exec_command("ls")
        return stdout.read()
    except paramiko.SSHException as e:
        return f"SSH connection failed: {str(e)}"


if __name__ == "__main__":
    # Set debug to False by default for production safety
    # For development, set FLASK_DEBUG=1 environment variable
    debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug_mode)