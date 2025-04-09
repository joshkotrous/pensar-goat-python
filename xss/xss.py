from flask import Flask, request
from markupsafe import escape
import os

app = Flask(__name__)


@app.route("/")
def home():
    """Protected from reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {escape(user_input)}!</h1>"  # Input is now sanitized

    return response  # User input is now properly escaped


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)