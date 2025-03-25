import openai
import os
import re

# Insecure API key handling (should use environment variables or a secure vault)
# This is kept for backward compatibility, but we recommend using environment variables
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def sanitize_input(user_input):
    """
    Sanitize user input to prevent prompt injection attacks.
    This is a basic implementation - more sophisticated methods may be needed
    based on the specific requirements.
    """
    # Remove any control characters that could affect prompt structure
    sanitized = re.sub(r'[\n\r\t]', ' ', user_input)
    
    # Limit input length to prevent extremely large prompts
    max_length = 500
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    
    return sanitized

def ai_agent(user_input):
    """A secured AI agent with protection against prompt injection."""
    # Sanitize the user input
    sanitized_input = sanitize_input(user_input)
    
    # Get API key from environment or fall back to the hardcoded one
    api_key = os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY)
    
    # Use ChatGPT's structured message format instead of f-string interpolation
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
        {"role": "user", "content": sanitized_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=api_key,
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))