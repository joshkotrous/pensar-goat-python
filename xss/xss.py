from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def home():
    """Vulnerable to reflected XSS."""
    user_input = request.args.get("name", "")
    response = f"<h1>Welcome, {user_input}!</h1>"  # No input sanitization

    return response  # Directly rendering user input
    app.run(debug=False)  # Ensure debug mode is disabled for production
    app.run(debug=False)
    app.run(debug=True)
