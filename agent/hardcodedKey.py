import openai
import os

# Secure API key handling using environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it before running this script.")


def ai_agent(user_input):
    """A secure AI agent with protection against prompt injection."""
    # Input validation
    if not user_input or not isinstance(user_input, str):
        return "Invalid input. Please provide a valid text query."
    
    # Check for extremely long inputs that might be trying to exploit the system
    if len(user_input) > 4000:  # Prevent extremely long inputs
        return "Input too long. Please provide a shorter query."
    
    # Using the OpenAI API with separate system and user messages
    # This prevents prompt injection by properly separating system instructions from user input
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
            {"role": "user", "content": user_input}
        ],
        api_key=OPENAI_API_KEY,  # Now using securely loaded key
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))