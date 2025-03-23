from flask import Flask, request
import html  # Add import for html.escape

app = Flask(__name__)


@app.route("/")
def home():
    """Previously vulnerable to reflected XSS, now fixed with HTML escaping."""
    user_input = request.args.get("name", "")
    # Sanitize user input using html.escape to prevent XSS
    safe_input = html.escape(user_input)
    response = f"<h1>Welcome, {safe_input}!</h1>"

    return response


if __name__ == "__main__":
    app.run(debug=True)