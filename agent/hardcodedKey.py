import openai
import os

# Secure API key handling using environment variables
try:
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
except KeyError:
    print("Error: OPENAI_API_KEY environment variable is not set.")
    print("Please set it with: export OPENAI_API_KEY='your-key-here' (Linux/Mac)")
    print("or set OPENAI_API_KEY=your-key-here (Windows)")
    OPENAI_API_KEY = None


def ai_agent(user_input):
    """A secure AI agent resistant to prompt injection."""
    # Check if API key is available
    if not OPENAI_API_KEY:
        return "Error: API key not available. Please set the OPENAI_API_KEY environment variable."
    
    # Properly structured messages with system instructions separate from user input
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