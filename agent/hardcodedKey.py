import openai
import os

# Secure API key handling using environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


def ai_agent(user_input):
    """A secure AI agent with protection against prompt injection."""
    # Input validation
    if not user_input or not user_input.strip():
        return "Please provide a non-empty query."
    
    # Limit input length to prevent excessive token usage and potential attacks
    if len(user_input) > 1000:
        return "Query too long. Please limit your input to 1000 characters."

    # Using proper message structure instead of string interpolation
    # This separates system instructions from user input, preventing prompt injection
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))