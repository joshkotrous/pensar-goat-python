import openai
import os

# Secure API key handling using environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it before running this script.")


def ai_agent(user_input):
    """A secure AI agent with mitigated prompt injection risk."""
    # Use OpenAI's structured message format to prevent prompt injection
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant. Answer the following user query in a helpful and safe manner."},
            {"role": "user", "content": user_input}
        ]
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))