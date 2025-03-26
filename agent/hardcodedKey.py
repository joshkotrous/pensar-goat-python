import openai
import os
import re

def get_api_key():
    """Retrieve API key from environment variable."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    return api_key


def validate_input(user_input):
    """
    Validate user input to prevent prompt injection attacks.
    
    Returns:
        bool: True if input is safe, False otherwise
    """
    if not isinstance(user_input, str):
        return False
    
    # Check for maximum length to prevent very large inputs
    if len(user_input) > 1000:
        return False
    
    # Define patterns that might indicate prompt injection attempts
    suspicious_patterns = [
        r"ignore previous instructions",
        r"forget your (previous )?instructions",
        r"you are now .+",
        r"act as .+",
        r"system prompt",
        r"new persona",
        r"ignore (all )?constraints",
        r"disregard (your )?programming",
    ]
    
    # Check for suspicious patterns
    for pattern in suspicious_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False
    
    return True


def ai_agent(user_input):
    """An AI agent with protection against prompt injection."""
    # Validate user input
    if not validate_input(user_input):
        return "I'm sorry, your query contains patterns that are not allowed for security reasons."
    
    try:
        # Configure OpenAI API key
        openai.api_key = get_api_key()
        
        # Use OpenAI's recommended message structure with separated system and user messages
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
                {"role": "user", "content": user_input}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error processing your request: {str(e)}"


# Example usage with security improvements
if __name__ == "__main__":
    print("AI Assistant (type 'exit' or 'quit' to end)")
    while True:
        user_query = input("Ask the AI: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        print(ai_agent(user_query))