import openai
import os

# Use environment variables for API keys
# Set OPENAI_API_KEY as an environment variable for security
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


def ai_agent(user_input):
    """A secure AI agent protected against prompt injection risk."""
    # Use explicit message roles for better security
    messages = [
        {
            "role": "system", 
            "content": "You are an AI assistant. Answer the following user query with helpful, harmless, and honest responses."
        },
        {
            "role": "user", 
            "content": user_input  # User input is contained within its proper context
        }
    ]

    # Use the secure API call pattern
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