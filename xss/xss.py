from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)


@app.route("/")
def home():
    """Previously vulnerable to reflected XSS, now fixed."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {escape(user_input)}!</h1>"  # User input sanitized with escape()

    return response  # User input is now properly escaped


if __name__ == "__main__":
    app.run(debug=True)