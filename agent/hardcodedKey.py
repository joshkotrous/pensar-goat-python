import openai
import os

# Get API key from environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def ai_agent(user_input):
    """An AI agent with improved security against prompt injection."""
    # Using the recommended message structure from OpenAI
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
        {"role": "user", "content": user_input}  # User input as separate message
    ]

    # Check if API key is available
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key not found in environment variables."

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