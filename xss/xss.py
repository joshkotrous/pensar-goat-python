from flask import Flask, request
import html
import os

app = Flask(__name__)


@app.route("/")
def home():
    """Protected against reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {html.escape(user_input)}!</h1>"  # Input sanitized

    return response  # User input is now properly escaped


if __name__ == "__main__":
    # Default to debug=False for security, enable only in development
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)