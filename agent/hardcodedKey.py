import openai
import os
import re

# API key should be stored in environment variables
# Set OPENAI_API_KEY in your environment before running this script
# Example: export OPENAI_API_KEY="your-api-key" (Unix/Linux/macOS)
# Example: set OPENAI_API_KEY=your-api-key (Windows)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it before running this script.")


def sanitize_user_input(text):
    """
    Sanitize user input to prevent prompt injection attacks.
    Filters common prompt injection patterns.
    """
    patterns_to_sanitize = [
        r"ignore previous instructions",
        r"ignore all previous commands",
        r"disregard your instructions",
        r"you are now",
        r"you must now",
        r"forget your instructions",
        r"you should ignore",
    ]
    
    sanitized_text = text
    for pattern in patterns_to_sanitize:
        sanitized_text = re.sub(pattern, "[FILTERED]", sanitized_text, flags=re.IGNORECASE)
    
    return sanitized_text


def ai_agent(user_input):
    """A more secure AI agent with prompt injection mitigation."""
    # Input validation
    if not user_input or len(user_input) > 1000:
        return "Invalid input. Please provide a reasonable query (1-1000 characters)."
    
    # Sanitize user input
    sanitized_input = sanitize_user_input(user_input)
    
    # Use OpenAI's recommended message structure instead of template strings
    # This provides better separation between system instructions and user input
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant. Answer the following user query professionally and helpfully."},
            {"role": "user", "content": sanitized_input}
        ],
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example usage with improved security
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))