import openai
import os
import re

# Use environment variable for API key instead of hardcoding
# Set your API key in your environment with: export OPENAI_API_KEY="your-api-key"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def sanitize_input(user_input):
    """
    Sanitize user input to prevent prompt injection.
    This is a basic implementation - in production, more sophisticated techniques may be needed.
    """
    # Remove any attempts to escape or inject system prompts
    sanitized = re.sub(r'(system:|assistant:|user:|\n#|\n\[|\n\{|\n\/\/|\n--)', '', user_input, flags=re.IGNORECASE)
    
    # Limit the length of user input to prevent excessive token usage
    max_length = 500  # Adjust based on your specific requirements
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "... (input truncated for security reasons)"
    
    return sanitized


def ai_agent(user_input):
    """A more secure AI agent with input validation and proper message structuring."""
    # Validate input is a string
    if not isinstance(user_input, str):
        return "Error: Invalid input type. Please provide a text query."
    
    # Check for empty input
    if not user_input.strip():
        return "Error: Empty input. Please provide a query."
    
    # Sanitize user input
    sanitized_input = sanitize_input(user_input)
    
    # Properly structure messages with system and user roles
    messages = [
        {
            "role": "system", 
            "content": "You are an AI assistant. Provide helpful, accurate, and ethical responses."
        },
        {
            "role": "user", 
            "content": sanitized_input
        }
    ]
    
    # Check if API key is available
    if not OPENAI_API_KEY:
        return "Error: API key not found. Please set the OPENAI_API_KEY environment variable."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=OPENAI_API_KEY,
        )
        
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        # In a production system, you would log the error
        return f"Error: Unable to process your request."


# Example usage with basic input validation
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))