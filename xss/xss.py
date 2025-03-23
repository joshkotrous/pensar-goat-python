from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)


@app.route("/")
def home():
    """Protected from reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {escape(user_input)}!</h1>"  # Input sanitized using escape

    return response  # User input is now sanitized


if __name__ == "__main__":
    app.run(debug=True)