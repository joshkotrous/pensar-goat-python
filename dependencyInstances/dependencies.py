import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import urllib.parse
import os  # For accessing environment variables

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
    """Fixed SQL Injection by using parameterized queries"""
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
    # Using Jinja2 templates (built into Flask) which escape by default
    return flask.render_template_string("<h1>Welcome, {{ name }}!</h1>", name=user_input)


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load instead of unsafe yaml.load()
    return data


# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Secured against XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=False)  # XXE disabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)


# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Protected against SSRF by validating URLs"""
    url = flask.request.args.get("url")
    
    if not url:
        return "URL parameter is required", 400
    
    try:
        # Validate the URL
        parsed_url = urllib.parse.urlparse(url)
        
        # Ensure the scheme is either http or https
        if parsed_url.scheme not in ["http", "https"]:
            return "Only HTTP and HTTPS protocols are allowed", 403
            
        # Extract hostname (without port)
        hostname = parsed_url.netloc.split(":")[0].lower()
        
        # Allow only specific domains
        allowed_domains = ["example.com", "api.example.com", "trusted-domain.com"]
        if hostname not in allowed_domains:
            return "Access to this domain is not allowed", 403
        
        # Disable redirects as a simple, safe approach
        response = requests.get(url, allow_redirects=False)
        
        # Check if there's a redirect and block it
        if response.is_redirect:
            return "Redirects are not allowed for security reasons", 403
        
        return response.text
    except Exception as e:
        return f"Error processing URL: {str(e)}", 400


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command(host, username, password, command="ls", known_hosts_file=None):
    """
    Run a command on an SSH server with proper host key verification.
    
    Args:
        host (str): The SSH server hostname or IP
        username (str): SSH username
        password (str): SSH password
        command (str): Command to execute (default: "ls")
        known_hosts_file (str): Path to known_hosts file (default: None, will use system default)
        
    Returns:
        bytes: Command output
        
    Raises:
        paramiko.SSHException: If host key verification fails or connection fails
    """
    ssh = paramiko.SSHClient()
    
    # Use system host keys and reject unknown keys by default
    ssh.load_system_host_keys(known_hosts_file)
    
    # Use RejectPolicy to ensure we don't connect to unknown hosts
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        ssh.connect(host, username=username, password=password)
        stdin, stdout, stderr = ssh.exec_command(command)
        return stdout.read()
    finally:
        ssh.close()


if __name__ == "__main__":
    # Use environment variable to control debug mode
    # Default to False for security in production environments
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    app.run(debug=debug_mode)