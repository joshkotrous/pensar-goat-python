import openai
import os

# Improved API key handling (using environment variables with fallback)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
if not OPENAI_API_KEY:

def ai_agent(user_input):
    """A more secure AI agent with protection against prompt injection."""
    # Input validation - basic checks to prevent non-string inputs
    if not isinstance(user_input, str):
        return "Invalid input. Please provide a valid query."
    
    # SECURITY FIX: Use proper message structure instead of embedding user input in a prompt
    # This separates system instructions from user input, mitigating prompt injection risks
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
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
    print(ai_agent(user_query))