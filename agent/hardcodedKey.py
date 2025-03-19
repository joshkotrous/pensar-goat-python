import openai
import os

# Secure API key handling using environment variables
# Set the OPENAI_API_KEY environment variable before running this script
# e.g., export OPENAI_API_KEY="your-api-key-here" (Linux/Mac)
# or set OPENAI_API_KEY="your-api-key-here" (Windows)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Check if the API key is available
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it before running this script.")


def ai_agent(user_input):
    """An AI agent that uses OpenAI API."""
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))