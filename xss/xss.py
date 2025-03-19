from flask import Flask, request
import html  # Import for HTML escaping

app = Flask(__name__)


@app.route("/")
def home():
    """Protected against reflected XSS."""
    user_input = request.args.get("name", "")
    # Escape the user input to prevent XSS
    escaped_input = html.escape(user_input)
    response = f"<h1>Welcome, {escaped_input}!</h1>"  

    return response  


if __name__ == "__main__":
    app.run(debug=True)