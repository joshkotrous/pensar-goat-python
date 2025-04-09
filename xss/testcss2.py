from flask import Flask, request
from html import escape
import os

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {escape(user_input)}!</h1>"  # Added HTML escaping for security

    return response  # User input is now properly escaped


if __name__ == "__main__":
    # Use environment variable to control debug mode, default to False for safety
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)