from flask import Flask, request
from markupsafe import escape
import os

app = Flask(__name__)


@app.route("/")
def home():
    """Protected against reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {escape(user_input)}!</h1>"  # Input sanitized with escape

    return response  # User input is now safely escaped


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode)