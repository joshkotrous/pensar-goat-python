import openai
import os

# Get API key from environment variables for better security
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
if not OPENAI_API_KEY:

def ai_agent(user_input):
    """A more secure AI agent with protection against prompt injection."""
    # Input validation
    if not isinstance(user_input, str):
        return "Error: Input must be a string"
    
    # Properly structure messages to prevent prompt injection
    # This separates system instructions from user content
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