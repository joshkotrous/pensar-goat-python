from flask import Flask, request
from markupsafe import escape  # Import escape from markupsafe
import os

app = Flask(__name__)


@app.route("/")
def home():
    """Protected against reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {escape(user_input)}!</h1>"  # Sanitize input with escape()

    return response  # Safely rendering user input


if __name__ == "__main__":
    # Get debug setting from environment variable, default to False
    debug_mode = os.environ.get("FLASK_DEBUG", "").lower() == "true"
    app.run(debug=debug_mode)