from flask import Flask, request
from markupsafe import escape
import os

app = Flask(__name__)


@app.route("/")
def home():
    """Previously vulnerable to reflected XSS, now fixed."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {escape(user_input)}!</h1>"  # Input sanitized with escape()

    return response


if __name__ == "__main__":
    # Get debug mode from environment variable, default to False for safety
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)