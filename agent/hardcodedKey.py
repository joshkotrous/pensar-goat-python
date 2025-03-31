import openai
import os
import re

# Secure API key handling with environment variables
# Make sure to set OPENAI_API_KEY in your environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

def validate_input(user_input):
    """
    Validate user input to prevent prompt injection and other malicious inputs.
    Returns (is_valid, reason) tuple.
    """
    if not user_input or user_input.strip() == "":
        return False, "Input cannot be empty."
    
    if len(user_input) > 1000:
        return False, "Input exceeds maximum length (1000 characters)."
    
    # Check for potential prompt injection attempts
    suspicious_patterns = [
        r"ignore previous instructions",
        r"disregard your guidelines",
        r"system: prompt",
        r"act as if",
        r"new persona"
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, user_input.lower()):
            return False, "Potentially unsafe input detected."
    
    return True, ""

def filter_output(output):
    """
    Apply safety filters to the AI's output before returning it to the user.
    Returns (is_safe, filtered_output) tuple.
    """
    # Check output length
    if len(output) > 2000:
        return False, "Response exceeded maximum length."
    
    # Check for unsafe content
    unsafe_patterns = [
        r"how to hack",
        r"illegal activities",
        r"harmful content"
    ]
    
    for pattern in unsafe_patterns:
        if re.search(pattern, output.lower()):
            return False, "Response contained potentially harmful content and was filtered."
    
    return True, output

def ai_agent(user_input):
    """An AI agent with improved security measures against prompt injection."""
    # Validate input
    is_valid, reason = validate_input(user_input)
    if not is_valid:
        return f"Error: {reason}"
    
    # Check if API key is available
    if not OPENAI_API_KEY:
        return "Error: API key not found. Please set the OPENAI_API_KEY environment variable."
    
    try:
        # Use separate system and user messages to reduce prompt injection risk
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an AI assistant. Answer the following user query professionally and accurately. Do not generate harmful, illegal, unethical or deceptive content."
                },
                {
                    "role": "user", 
                    "content": user_input
                }
            ],
            api_key=OPENAI_API_KEY,
        )
        
        output = response["choices"][0]["message"]["content"]
        
        # Apply output filters
        is_safe, filtered_output = filter_output(output)
        if not is_safe:
            return f"Error: {filtered_output}"
        
        return filtered_output
    
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Example usage with improved security
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))