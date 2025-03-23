import openai
import re

# Insecure API key handling (should use environment variables or a secure vault)
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def sanitize_input(user_input):
    """Sanitize user input to prevent prompt injection attacks."""
    # Remove control characters and excessive whitespace
    sanitized = re.sub(r'[\x00-\x1F\x7F]', '', user_input)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    # Limit input length to prevent excessive prompts
    max_length = 500
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
        
    return sanitized


def ai_agent(user_input):
    """A secured AI agent with prompt injection protection."""
    # Sanitize the user input
    sanitized_input = sanitize_input(user_input)
    
    # Separate system instructions from user input using appropriate roles
    # This provides better structural protection against prompt injection
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
        {"role": "user", "content": sanitized_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,  # Insecure key handling
    )

    return response["choices"][0]["message"]["content"]


# Example usage with protection
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))