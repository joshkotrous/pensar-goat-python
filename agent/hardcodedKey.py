import openai

# Insecure API key handling (should use environment variables or a secure vault)
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

def validate_user_input(user_input):
    """
    Validate user input to detect potential prompt injection attempts.
    Returns sanitized input or raises an exception.
    """
    # Check for empty input
    if not user_input or user_input.strip() == "":
        raise ValueError("Input cannot be empty")
    
    # Check for common prompt injection patterns
    suspicious_phrases = [
        "ignore previous instructions",
        "disregard previous instructions",
        "disregard all instructions",
        "disregard your instructions",
        "ignore all previous instructions",
        "ignore all above instructions",
        "forget your instructions",
        "do not follow your instructions",
    ]
    
    for phrase in suspicious_phrases:
        if phrase in user_input.lower():
            raise ValueError("Potential prompt injection detected")
    
    # Basic sanitation - limit length
    max_length = 1000
    if len(user_input) > max_length:
        return user_input[:max_length] + "... (truncated)"
    
    return user_input

def ai_agent(user_input):
    """An AI agent with protection against prompt injection risk."""
    try:
        # Validate and sanitize user input
        sanitized_input = validate_user_input(user_input)
        
        # Separate system instructions from user input using proper message structure
        messages = [
            {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
            {"role": "user", "content": sanitized_input}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=OPENAI_API_KEY,
        )

        return response["choices"][0]["message"]["content"]
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))