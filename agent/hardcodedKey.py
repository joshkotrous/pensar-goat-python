import openai
import os

# Use environment variables for API key instead of hardcoding
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")


def ai_agent(user_input):
    """An AI agent with protection against prompt injection risk."""
    # Basic input validation
    if not user_input or user_input.isspace():
        return "Error: Please provide a valid query."
    
    # Limit input length to prevent abuse
    max_length = 1000
    if len(user_input) > max_length:
        user_input = user_input[:max_length] + "... (input truncated due to length)"
    
    # Use the proper message structure instead of string interpolation
    messages = [
        {"role": "system", "content": "You are an AI assistant. Answer the following user query:"},
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
        # Basic error handling
        return f"Error: Could not process your request. {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": processed_input}
            ],
            api_key=OPENAI_API_KEY,  # Insecure key handling
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error processing your request: {str(e)}"


# Example vulnerable usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))