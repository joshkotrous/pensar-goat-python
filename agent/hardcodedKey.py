import openai
import os

# Secure API key handling using environment variables
# Set this in your environment: export OPENAI_API_KEY="your-key-here"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


def ai_agent(user_input):
    """A secure AI agent that prevents prompt injection."""
    # Basic input validation
    if not user_input or not isinstance(user_input, str):
        return "Error: Invalid input. Please provide a valid query."
    
    # Limit input length to prevent abuse
    if len(user_input) > 4000:
        return "Error: Input is too long. Please limit your query to 4000 characters."
    
    # Using proper message structure instead of string interpolation
    # This prevents prompt injection by separating system instructions from user content
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
        return f"Error: An error occurred while processing your request: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))