import openai
import os
import re

# Use environment variables for API credentials
# Set this with: export OPENAI_API_KEY="your-key-here"
# or in Windows: set OPENAI_API_KEY=your-key-here


def validate_input(user_input):
    """
    Validate and sanitize user input to prevent prompt injection.
    """
    if not user_input or not user_input.strip():
        return "Empty input is not allowed."
    
    # Trim whitespace
    sanitized = user_input.strip()
    
    # Remove potential control characters and non-printable characters
    sanitized = re.sub(r'[^\x20-\x7E\s]', '', sanitized)
    
    # Limit input length to prevent token abuse
    max_length = 500
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "... (input truncated)"
    
    return sanitized


def ai_agent(user_input):
    """A secured AI agent that validates input and uses proper message formatting."""
    # Get API key from environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return "Error: API key not found in environment variables. Please set OPENAI_API_KEY."
    
    # Validate and sanitize input
    validated_input = validate_input(user_input)
    
    # Use proper message structure with separate system and user messages
    # This is more secure than formatting a prompt string with user input
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
        {"role": "user", "content": validated_input}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=api_key,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error communicating with the AI service: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))