import openai
import os

# Use environment variables for API key security
# Fallback to hardcoded key for backward compatibility
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


def ai_agent(user_input):
    """A secure AI agent with protection against prompt injection risk."""
    # Basic input validation
    if not user_input or len(user_input) > 1000:
        return "Input is empty or too long. Please provide a shorter query."
    
    # List of terms that might indicate prompt injection attempts
    dangerous_terms = [
        "ignore previous instructions",
        "ignore all previous",
        "system:",
        "system prompt:",
        "you are now",
        "your role is"
    ]
    
    for term in dangerous_terms:
        if term.lower() in user_input.lower():
            return "Your input contains disallowed terms. Please try again."
    
    # Use OpenAI's message structure to properly separate system and user messages
    # This prevents prompt injection by separating system instructions from user input
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
        {"role": "user", "content": user_input}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
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