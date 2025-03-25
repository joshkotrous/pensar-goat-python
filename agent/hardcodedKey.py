import openai
import os
import re

# Use environment variable for API key instead of hardcoding
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

def sanitize_input(user_input):
    """Sanitize user input to prevent prompt injection attacks."""
    # Remove potentially dangerous sequences and limit input length
    sanitized = re.sub(r'[\\"`\']', '', user_input)
    max_length = 500
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "... (truncated)"
    return sanitized

def validate_input(user_input):
    """Validate user input for suspicious patterns."""
    suspicious_patterns = [
        r"ignore previous instructions",
        r"disregard",
        r"system prompt",
        r"new instructions",
        r"AI: ",
        r"Assistant: ",
        r"System: ",
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False
    return True

def ai_agent(user_input):
    """A more secure AI agent with protection against prompt injection."""
    # Validate and sanitize input
    if not validate_input(user_input):
        return "I cannot process this request as it contains potentially harmful patterns."
    
    sanitized_input = sanitize_input(user_input)
    
    # Using proper message structure to separate system instructions from user input
    messages = [
        {
            "role": "system", 
            "content": "You are an AI assistant. Answer the following user query:"
        },
        {
            "role": "user", 
            "content": sanitized_input
        }
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