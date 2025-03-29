from flask import Flask, request
import html
import os

app = Flask(__name__)


@app.route("/")
def home():
    """Protected against reflected XSS."""
    user_input = request.args.get("name", "")
    sanitized_input = html.escape(user_input)
    response = f"<h1>Welcome, {sanitized_input}!</h1>"  # Input is now sanitized

    return response  # Safely rendering user input


if __name__ == "__main__":
    debug_mode = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
    app.run(debug=debug_mode)