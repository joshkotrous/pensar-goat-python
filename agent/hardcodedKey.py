import openai
import os
import re

# Use environment variables for API key, but maintain backward compatibility
# In production, store keys securely in environment variables or secret management systems
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

def sanitize_input(user_input):
    """Sanitize user input to prevent prompt injection."""
    # Limit length to prevent excessive inputs
    if len(user_input) > 1000:
        user_input = user_input[:1000] + "... (input truncated for security reasons)"
    
    # Remove control characters that might interfere with prompt formatting
    user_input = re.sub(r'[\x00-\x1F\x7F]', '', user_input)
    
    # Check for common prompt injection patterns
    injection_patterns = [
        r'ignore (all|previous) instructions',
        r'forget (all|previous) instructions',
        r'disregard (all|previous) instructions',
        r'system prompt:',
        r'you are now [^.]{10,}',
        r'new instructions:',
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return "Input contains potentially harmful instructions. Please rephrase your question."
    
    return user_input

def ai_agent(user_input):
    """A secure AI agent with protection against prompt injection."""
    # Sanitize user input
    sanitized_input = sanitize_input(user_input)
    
    # If sanitization returned an error message, return it
    if "potentially harmful instructions" in sanitized_input:
        return sanitized_input
    
    # Use a more secure approach with separate system and user messages
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
                {"role": "user", "content": sanitized_input}
            ],
            api_key=OPENAI_API_KEY,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error communicating with OpenAI: {str(e)}"

# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))