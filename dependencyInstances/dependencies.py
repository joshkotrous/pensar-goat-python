import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import os

app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # Required for Flask 1.0+ permanent sessions

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
@app.route("/")

# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    """Vulnerable to XSS"""
    user_input = flask.request.args.get("name", "")
    return (
        f"<h1>Welcome, {user_input}!</h1>"  # No sanitization, allowing script injection
    )
# ======== 3. Arbitrary Code Execution via YAML ========

# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.load(file, Loader=yaml.Loader)  # Using unsafe yaml.load()
    return data
# ======== 4. External XML Entity (XXE) Attack ========

# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Vulnerable to XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=True)  # XXE enabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)
# ======== 5. Insecure Request Handling ========

# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Vulnerable to credential leakage in redirects"""
    url = flask.request.args.get("url")
    response = requests.get(url, allow_redirects=True)
    return response.text
        return "Error: No URL provided", 400

# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command():
    """Vulnerable to RCE if connecting to an untrusted SSH server"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )  # Automatically accepting any key
    ssh.auth_timeout = 30  # Add explicit authentication timeout
    stdin, stdout, stderr = ssh.exec_command("ls")
    return stdout.read()
        # Handle SSH exceptions, e.g., unknown host key

if __name__ == "__main__":
    app.run(debug=True)
    app.run(debug=debug_mode)

if __name__ == "__main__":
    app.run(debug=True)
        # Check if it's an IP address
        try:
            ip = ipaddress.ip_address(hostname)
            # Check if it's a private IP
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return "Error: Access to internal networks denied", 403
        except ValueError:
            # Not an IP address, check domain
            if not any(hostname == domain or hostname.endswith('.' + domain) for domain in allowed_domains):
                return f"Error: Domain '{hostname}' not in allowed list", 403
            
            # Resolve domain to IP and check again (prevent DNS rebinding)
            try:
                ip = ipaddress.ip_address(socket.gethostbyname(hostname))
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    return "Error: Domain resolves to internal network", 403
            except (socket.error, ValueError):
                return "Error: Unable to resolve domain", 400
                
        # Make the request with additional security parameters
        headers = {
            'User-Agent': 'SecureApplication/1.0',
            # Add authentication if needed for specific APIs
            # 'Authorization': 'Bearer YOUR_API_KEY'
        }
        
        response = requests.get(
            url, 
            allow_redirects=True,
            timeout=10,  # Set a timeout
            verify=True,  # Verify SSL certificates
            headers=headers
        )
        
        # Instead of returning raw response, process it safely
        safe_response = {
            'status_code': response.status_code,
            'content_type': response.headers.get('Content-Type', ''),
            'content_length': len(response.content),
            # Sanitize or limit the actual content based on your application needs
            'preview': response.text[:200] if response.text else ''  # Only return preview
        }
        
        return flask.jsonify(safe_response)
    
    except Exception as e:
        return f"Error processing request: {str(e)}", 500


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