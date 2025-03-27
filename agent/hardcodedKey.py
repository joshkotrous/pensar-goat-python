import openai
import os
import re

# Get API key from environment variable with fallback
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
# Warning if using default key
if OPENAI_API_KEY == "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
    print("Warning: Using default API key. Set OPENAI_API_KEY environment variable for production use.")


def sanitize_input(user_input):
    """Sanitize user input to prevent prompt injection attacks."""
    if not isinstance(user_input, str):
        return str(user_input)
    
    # Remove control characters that could manipulate prompt structure
    sanitized = re.sub(r'[\n\r\t]', ' ', user_input)
    
    # Limit input length
    max_length = 500
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    
    return sanitized


def ai_agent(user_input):
    """An AI agent with mitigations against prompt injection risk."""
    # Input validation and sanitization
    if not user_input or (isinstance(user_input, str) and user_input.strip() == ""):
        return "Please provide a valid query."
    
    sanitized_input = sanitize_input(user_input)
    
    # Use the OpenAI API with proper message structure to mitigate prompt injection
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system", 
                "content": "You are an AI assistant. Answer the following user query."
            },
            {
                "role": "user",
                "content": sanitized_input
            }
        ],
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))