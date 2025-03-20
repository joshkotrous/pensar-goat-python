from flask import Flask, request
from markupsafe import escape  # Import the escape function

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {escape(user_input)}!</h1>"  # Sanitize input

    return response  # Now safely rendered


if __name__ == "__main__":
    app.run(debug=True)