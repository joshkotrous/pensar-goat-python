from flask import Flask, request
from markupsafe import escape  # Import escape function from markupsafe (included with Flask)

app = Flask(__name__)


@app.route("/")
def home():
    """Protected against reflected XSS."""
    user_input = request.args.get("name", "")
    # Escape user input to prevent XSS
    safe_input = escape(user_input)
    response = f"<h1>Welcome, {safe_input}!</h1>"  # Input is now sanitized

    return response  # Safely rendering user input


if __name__ == "__main__":
    app.run(debug=True)