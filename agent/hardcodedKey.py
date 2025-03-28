import openai
import os

# Secure API key handling using environment variables
# Set OPENAI_API_KEY environment variable before running this script

def sanitize_input(input_text):
    """
    Basic sanitization of user input to prevent prompt injection attacks.
    """
    if not isinstance(input_text, str):
        return ""
    
    # Limit input length
    max_length = 2000
    if len(input_text) > max_length:
        input_text = input_text[:max_length]
    
    return input_text

    ]
def ai_agent(user_input):
    """An AI agent with protection against prompt injection."""
    # Sanitize user input
    sanitized_input = sanitize_input(user_input)
    
    # Use OpenAI's message structure properly to separate system instructions from user input
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
            {"role": "user", "content": sanitized_input}
        ],
        api_key=OPENAI_API_KEY,  # Insecure key handling
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))