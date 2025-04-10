import sqlite3
import yaml  # Vulnerable to arbitrary code execution
import flask  # Vulnerable Flask version
import requests  # Vulnerable requests version
import paramiko  # Vulnerable to RCE in older versions
import lxml.etree as ET  # Vulnerable to XXE attacks

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
    """Protected against SQL Injection using parameterized queries"""
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
    return (
        f"<h1>Welcome, {user_input}!</h1>"  # No sanitization, allowing script injection
    )


# ======== 3. Arbitrary Code Execution via YAML ========
def load_config():
    """Loads configuration from a YAML file safely"""
    with open("config.yaml", "r") as file:
        data = yaml.safe_load(file)  # Using safe_load to prevent code execution
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
@app.route("/fetch")
def fetch():
    """Vulnerable to credential leakage in redirects"""
    url = flask.request.args.get("url")
    response = requests.get(url, allow_redirects=True)
    return response.text


# ======== 6. Remote Code Execution via Paramiko ========
def run_ssh_command(host, command, username=None, password=None, key_filename=None, auto_add_policy=False):
    """Execute a command on a remote server via SSH with proper host key verification.
    
    Args:
        host (str): The remote host to connect to.
        command (str): The command to execute.
        username (str, optional): SSH username.
        password (str, optional): SSH password.
        key_filename (str, optional): Path to private key file.
        auto_add_policy (bool, optional): Whether to automatically add unknown host keys.
            Default is False for security.
    
    Returns:
        str: Command output or error message.
    """
    try:
        ssh = paramiko.SSHClient()
        # Load system host keys first
        ssh.load_system_host_keys()
        
        # Only use AutoAddPolicy if explicitly requested, otherwise use RejectPolicy
        if auto_add_policy:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        else:
            ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
        
        # Connect with the provided credentials
        connect_kwargs = {
            "hostname": host,
        }
        
        if username:
            connect_kwargs["username"] = username
        if password:
            connect_kwargs["password"] = password
        if key_filename:
            connect_kwargs["key_filename"] = key_filename
            
        ssh.connect(**connect_kwargs)
        
        # Execute the command
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode('utf-8')
        
        return output
    except paramiko.SSHException as e:
        return f"SSH Error: {str(e)}"
    except paramiko.AuthenticationException:
        return "Authentication failed"
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if 'ssh' in locals():
            ssh.close()


if __name__ == "__main__":
    app.run(debug=True)