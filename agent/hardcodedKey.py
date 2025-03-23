import openai
import re

# Insecure API key handling (should use environment variables or a secure vault)
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def validate_user_input(user_input):
    """
    Validates user input to prevent prompt injection attacks.
    Returns True if input is safe, False otherwise.
    """
    # Reject empty inputs
    if not user_input or not user_input.strip():
        return False
    
    # Check for attempts to override system instructions
    dangerous_patterns = [
        r"ignore (?:previous|prior|earlier|above) (?:instructions|prompts|directives|commands)",
        r"disregard (?:previous|prior|earlier|above) (?:instructions|prompts|directives|commands)",
        r"forget (?:previous|prior|earlier|above) (?:instructions|prompts|directives|commands)",
        r"(?:system|assistant|AI):\s",
        r"you (?:are|should|must) (?:not|no longer) (?:an AI assistant|behave like|act as)",
        r"new\s+instructions:",
        r"please\s+(?:ignore|disregard)\s+.*and\s+instead",
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False
    
    # Limit input length to prevent excessive tokens
    if len(user_input) > 2000:
        return False
    
    return True


def ai_agent(user_input):
    """A more secure AI agent with prompt injection protection."""
    # Validate user input before processing
    if not validate_user_input(user_input):
        return "I'm sorry, that input contains patterns that may affect system behavior. Please try a different query."
    
    # Use separate messages for system and user content instead of embedding user input in the prompt
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
            {"role": "user", "content": user_input}
        ],
        api_key=OPENAI_API_KEY,  # Insecure key handling
    )

    return response["choices"][0]["message"]["content"]


# Example usage with improved security
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))