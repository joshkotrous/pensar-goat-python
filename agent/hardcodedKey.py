import openai
import os
import re


# Secure API key handling using environment variables
# Set OPENAI_API_KEY as an environment variable before running
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def validate_user_input(user_input):
    """Validate user input to prevent prompt injection."""
    # Check for empty input
    if not user_input or user_input.strip() == "":
        return False
    
    # Check if input is too long
    if len(user_input) > 1000:
        return False
    
    # Check for suspicious patterns that might indicate prompt injection
    suspicious_patterns = [
        r"ignore .*previous.*instructions",
        r"disregard .*previous.*instructions",
        r"forget .*previous.*instructions",
        r"instead .*(do|tell|say|give|provide)",
        r"system prompt",
        r"you are now",
        r"new role",
        r"you (will|must|should) (now|instead)"
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, user_input.lower()):
            return False
    
    return True


def ai_agent(user_input):
    """A more secure AI agent with prompt injection mitigations."""
    # Check if API key is available
    if not OPENAI_API_KEY:
        return "Error: OpenAI API key not found in environment variables. Please set the OPENAI_API_KEY environment variable."
    
    # Validate user input before processing
    if not validate_user_input(user_input):
        return "I'm sorry, I cannot process that request."
    
    # Use a more structured approach instead of direct interpolation
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example usage with improved security
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))