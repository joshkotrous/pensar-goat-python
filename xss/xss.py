from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)


@app.route("/")
def home():
    """Protected against reflected XSS."""
    user_input = request.args.get("name", "")
    # Sanitize user input to prevent XSS
    sanitized_input = escape(user_input)
    response = f"<h1>Welcome, {sanitized_input}!</h1>"

    return response


if __name__ == "__main__":
    app.run(debug=True)