from flask import Flask, request
import html

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {html.escape(user_input)}!</h1>"  # Added HTML escaping

    return response  # User input is now escaped


if __name__ == "__main__":
    app.run(debug=True)