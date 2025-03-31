import openai
import os

# Retrieve API key from environment variables instead of hardcoding
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API key. Set the OPENAI_API_KEY environment variable.")


def ai_agent(user_input):
    """A secure AI agent with protection against prompt injection."""
    # Input validation
    if not isinstance(user_input, str):
        raise TypeError("User input must be a string")
    
    # Use OpenAI's message structure with separate roles to prevent prompt injection
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
    try:
        print(ai_agent(user_query))
    except Exception as e:
        print(f"An error occurred: {e}")