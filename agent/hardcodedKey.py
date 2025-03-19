import openai
import os
import re

# Secure API key handling using environment variables
def get_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return api_key


def validate_user_input(user_input):
    """Validate and sanitize user input to prevent prompt injection."""
    # Check if input is a string
    if not isinstance(user_input, str):
        return False, "Input must be a string"
    
    # Check if input is empty
    if not user_input.strip():
        return False, "Input cannot be empty"
    
    # Basic sanitization to prevent prompt injection attempts
    patterns_to_sanitize = [
        (r"system:", "[filtered]"),
        (r"assistant:", "[filtered]"),
        (r"AI:", "[filtered]"),
        (r"<.*?>", ""),  # Remove simple HTML/XML tags
    ]
    
    sanitized_input = user_input
    for pattern, replacement in patterns_to_sanitize:
        sanitized_input = re.sub(pattern, replacement, sanitized_input, flags=re.IGNORECASE|re.DOTALL)
    
    # Limit input length
    max_length = 500
    if len(sanitized_input) > max_length:
        sanitized_input = sanitized_input[:max_length] + "..."
    
    return True, sanitized_input.strip()


def ai_agent(user_input):
    """A more secure AI agent with input validation and proper prompt structure."""
    # Validate and sanitize input
    is_valid, processed_input = validate_user_input(user_input)
    
    if not is_valid:
        return f"Error: {processed_input}"
    
    # Using proper message structure for OpenAI API
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query appropriately."},
        {"role": "user", "content": processed_input}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=get_api_key(),
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error communicating with AI service: {str(e)}"


# Example usage
if __name__ == "__main__":
    print("Type 'exit' or 'quit' to end the conversation.")
    while True:
        user_query = input("Ask the AI: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        print(ai_agent(user_query))