import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks
import os  # Added for environment variable access

app = flask.Flask(__name__)

# ======== 1. SQL Injection Vulnerability ========
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()
cursor.execute(
    "CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)"
)
cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'password123')")
conn.commit()
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
    return "Invalid credentials."

# ======== 2. XSS Vulnerability ========
@app.route("/")
def home():
    """Vulnerable to XSS"""
    user_input = flask.request.args.get("name", "")
    return (
        f"<h1>Welcome, {user_input}!</h1>"  # No sanitization, allowing script injection
    )
    )

# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Vulnerable to Arbitrary Code Execution"""
    with open("config.yaml", "r") as file:
        data = yaml.load(file, Loader=yaml.Loader)  # Using unsafe yaml.load()
    return data
    return data

# ======== 4. External XML Entity (XXE) Attack ========
@app.route("/upload_xml", methods=["POST"])
def upload_xml():
    """Vulnerable to XXE"""
    xml_data = flask.request.data
    parser = ET.XMLParser(resolve_entities=True)  # XXE enabled
    tree = ET.fromstring(xml_data, parser)
    return ET.tostring(tree)
    return ET.tostring(tree)

# ======== 5. Insecure Request Handling ========
@app.route("/fetch")
def fetch():
    """Vulnerable to credential leakage in redirects"""
    url = flask.request.args.get("url")
    response = requests.get(url, allow_redirects=True)
    return response.text
    # Input validation - ensure the URL is not empty and is a valid URL

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
    try:

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)
    except paramiko.SSHException as e:
        # Handle SSH exceptions (including unknown host keys)
        return f"SSH Error: {str(e)}"
    except Exception as e:
        # Handle other exceptions
        return f"Error: {str(e)}"
    finally:
        ssh.close()


if __name__ == "__main__":
    app.run(debug=True)
        current_url = url
        max_redirects = 3
        redirect_count = 0
        
        while redirect_count <= max_redirects:
            response = requests.get(current_url, allow_redirects=False, timeout=5)
            
            # If not a redirect, return the response
            if response.status_code < 300 or response.status_code >= 400:
                return response.text
            
            # Handle redirect
            if 'Location' in response.headers:
                redirect_url = response.headers['Location']
                
                # Handle relative URLs
                if not redirect_url.startswith(('http://', 'https://')):
                    # Convert relative URL to absolute
                    redirect_url = urllib.parse.urljoin(current_url, redirect_url)
                
                if not is_url_safe(redirect_url):
                    return "Redirect to forbidden URL", 403
                
                current_url = redirect_url
                redirect_count += 1
            else:
                # Redirect without Location header
                return "Invalid redirect", 400
        
        return "Too many redirects", 400
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