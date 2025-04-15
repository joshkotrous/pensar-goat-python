from flask import Flask, request
import html  # Import the html module for escaping

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    safe_input = html.escape(user_input)  # Sanitize user input
    response = f"<h1>Welcome, {safe_input}!</h1>"  

    return response  


if __name__ == "__main__":
    app.run(debug=True)
