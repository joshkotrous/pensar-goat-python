import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
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

# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    """Vulnerable to XSS"""
    user_input = flask.request.args.get("name", "")
    return (
        f"<h1>Welcome, {user_input}!</h1>"  # No sanitization, allowing script injection
    )
def load_config():

# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.load(file, Loader=yaml.Loader)  # Using unsafe yaml.load()
    return data
@app.route("/upload_xml", methods=["POST"])

# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Vulnerable to XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=True)  # XXE enabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)
@app.route("/fetch")

# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Safely handles external requests"""
    url = flask.request.args.get("url")
    
    # Validate URL to prevent SSRF or Open Redirect
    if not url:
        return "No URL provided", 400
def run_ssh_command(server="trusted-server.com", username="user", command="ls", key_path=None, password="pass"):
    """Secure connection to a trusted SSH server"""
    allowed_domains = ["trusted-domain.com", "api.trusted-service.org"]
    
    # Load host keys from the user's known_hosts file
    ssh.load_system_host_keys()
    
    # Set a strict host key policy
    ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
    
    try:
        # Connect to the server with key-based auth if key_path is provided, else with password
        if key_path:
            ssh.connect(server, username=username, key_filename=key_path)
        elif password:
            ssh.connect(server, username=username, password=password)
        else:
            raise ValueError("Either key_path or password must be provided")
        
        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read()
        
        # Close the connection
        ssh.close()
        
        return result
    except paramiko.SSHException as e:
        # Handle SSH exceptions
        return f"SSH Error: {str(e)}"
    except Exception as e:
        # Handle other exceptions
        return f"Error: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)