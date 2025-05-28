from flask import Flask, request
import html

app = Flask(__name__)


@app.route("/")
def home():
    """Safe from reflected XSS."""
    user_input = request.args.get("name", "")
    safe_user_input = html.escape(user_input)
    response = f"<h1>Welcome, {safe_user_input}!</h1>"

    return response


if __name__ == "__main__":
    app.run(debug=True)