from flask import Flask, request
import html

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    # Escape HTML special characters in user_input to prevent XSS
    sanitized_input = html.escape(user_input)
    response = f"<h1>Welcome, {sanitized_input}!</h1>"

    return response  # Directly rendering user input


if __name__ == "__main__":
    app.run(debug=True)