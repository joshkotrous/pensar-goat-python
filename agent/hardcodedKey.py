import openai
import os

# Retrieve API key from environment variable with fallback to original hardcoded key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
if not OPENAI_API_KEY:

def ai_agent(user_input):
    """A more secure AI agent with proper message structure."""
    # Use OpenAI's structured message format instead of string interpolation
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query."},
        {"role": "user", "content": user_input}
    ]
    
    # Limit input length to prevent complex injection attacks
    if len(user_input) > 1000:
        messages=messages,
        api_key=OPENAI_API_KEY,
    # Use OpenAI's recommended message structure with separate system and user roles
    # This approach is more resistant to prompt injection than embedding user input in a template
    messages = [
        {"role": "system", "content": "You are an AI assistant that provides helpful, accurate, and safe information."},
        {"role": "user", "content": user_input}
# Example usage

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
    
    try:
        print(ai_agent(user_query))
    except Exception as e:
        print(f"Error: {e}")
    except Exception as e:
        return f"Error processing request: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))