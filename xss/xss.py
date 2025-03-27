from flask import Flask, request
from markupsafe import escape  # Import escape function

app = Flask(__name__)


@app.route("/")
def home():
    """Protected against reflected XSS."""
    user_input = request.args.get("name", "")
    # Escaping user input to prevent XSS
    safe_input = escape(user_input)
    response = f"<h1>Welcome, {safe_input}!</h1>"

    return response

    # Use environment variable to control debug mode, default to False for production safety
if __name__ == "__main__":
    app.run(debug=True)