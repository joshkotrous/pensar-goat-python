from flask import Flask, request
from markupsafe import escape
import os

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    safe_input = escape(user_input)
    response = f"<h1>Welcome, {safe_input}!</h1>"

    return response


if __name__ == "__main__":
    # Get debug setting from environment variable, default to False
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)