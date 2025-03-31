import openai
import os
import re

# Use environment variables for API keys
try:
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
except KeyError:
    raise RuntimeError("Environment variable OPENAI_API_KEY not set. Please set it to your OpenAI API key.")

def validate_user_input(user_input):
    """Validate user input to prevent prompt injection attacks."""
    # Basic validation checks
    if not user_input or user_input.strip() == "":
        return False, "Input cannot be empty."
    
    # Check for potentially malicious patterns
    suspicious_patterns = [
        r"ignore previous instructions",
        r"disregard",
        r"system role",
        r"new instructions",
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False, "Input contains potentially harmful instructions."
    
    # Length check to prevent very long inputs
    if len(user_input) > 500:
        return False, "Input exceeds maximum allowed length."
    
    return True, ""

def ai_agent(user_input):
    """A secure AI agent with prompt injection protection."""
    # Validate input
    is_valid, error_message = validate_user_input(user_input)
    if not is_valid:
        return f"Error: {error_message}"
    
    try:
        # Use proper message structure instead of string interpolation
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
                {"role": "user", "content": user_input}
            ],
            api_key=OPENAI_API_KEY,
        )
        
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error processing your request: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))