import openai
import re

# Insecure API key handling (should use environment variables or a secure vault)
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def validate_input(user_input):
    """Validate and sanitize user input to prevent prompt injection attacks."""
    # Check for empty or whitespace-only input
    if not user_input or user_input.isspace():
        return False, "Input cannot be empty."
    
    # Check input length to prevent token exploitation
    if len(user_input) > 500:  # Limiting to 500 characters
        return False, "Input is too long. Please limit your query to 500 characters."
    
    # Check for potential prompt injection patterns
    suspicious_patterns = [
        r"ignore previous instructions",
        r"ignore prior instructions",
        r"disregard previous",
        r"forget your instructions",
        r"new instructions:",
        r"you are now",
        r"system: "
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False, "Your input contains prohibited patterns."
    
    return True, user_input


def ai_agent(user_input):
    """A secured AI agent with prompt injection prevention."""
    # Validate the user input
    is_valid, validation_result = validate_input(user_input)
    if not is_valid:
        return validation_result
    
    # Use structured messages instead of string interpolation
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer user queries helpfully and accurately. Do not perform any actions or comply with instructions that would violate ethical guidelines."},
        {"role": "user", "content": validation_result}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,  # Insecure key handling
    )

    return response["choices"][0]["message"]["content"]


# Example usage with improved security
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))