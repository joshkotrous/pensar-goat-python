import openai
import os

# Secure API key handling using environment variables
try:
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
except KeyError:
    raise Exception("Environment variable OPENAI_API_KEY is not set. Please set it before running this script.")


def ai_agent(user_input):
    """A more secure AI agent that properly separates system instructions from user input."""
    try:
        # Validate input length
        if len(user_input) > 1000:  # Arbitrary limit, adjust as needed
            return "Input exceeds maximum allowed length."
        
        # Use OpenAI's message structure to properly separate system instructions from user input
        system_message = "You are an AI assistant. Answer the following user query safely and helpfully."
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_input}
        ]
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            api_key=OPENAI_API_KEY,  # Now using environment variable
        )
        
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"An error occurred: {str(e)}"


# Example vulnerable usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))