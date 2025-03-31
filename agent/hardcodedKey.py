import openai
import re
import os

# Use environment variable for API key instead of hardcoding
# Set OPENAI_API_KEY in your environment variables for security


def validate_user_input(input_text):
    """
    Validates user input to prevent prompt injection attacks.
    
    Args:
        input_text (str): The user input to validate
        
    Returns:
        tuple: (is_valid, result_or_error_message)
    """
    # Check for suspicious patterns that might indicate injection attempts
    suspicious_patterns = [
        r"ignore previous instructions",
        r"disregard your guidelines",
        r"forget your training",
        r"system prompt",
        r"you are now",
        r"new role",
        r"your new task",
        r"override previous",
        r"you must now"
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, input_text, re.IGNORECASE):
            return False, "Potentially harmful input detected"
    
    # Check input length to prevent excessively large prompts
    if len(input_text) > 1000:
        return False, "Input exceeds maximum allowed length"
    
    # If all checks pass, return the validated input
    return True, input_text


def ai_agent(user_input):
    """A secure AI agent with input validation to prevent prompt injection."""
    # Validate user input
    is_valid, result = validate_user_input(user_input)
    
    if not is_valid:
        return f"Error: {result}"
    
    # Using OpenAI's message structure more securely
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return "Error: API key not found in environment variables"
            
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that provides helpful answers."},
                {"role": "user", "content": result}
            ],
            api_key=api_key
        )
        
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error processing request: {str(e)}"


# Example usage with added error handling
if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set. Please set it before running this script.")
        print("Example: export OPENAI_API_KEY='your-api-key-here'")
        exit(1)
        
    while True:
        try:
            user_query = input("Ask the AI: ")
            if user_query.lower() in ["exit", "quit"]:
                break
            print(ai_agent(user_query))
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An error occurred: {str(e)}")