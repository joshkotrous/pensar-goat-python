import openai
import os

# Get API key from environment variable instead of hardcoding it
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def ai_agent(user_input):
    """A more secure AI agent that prevents prompt injection."""
    if not OPENAI_API_KEY:
        return "Error: API key not found. Please set the OPENAI_API_KEY environment variable."
    
    # Define system message separately from user input
    system_message = {
        "role": "system", 
        "content": "You are an AI assistant. Answer the following user query."
    }
    
    # User input in a separate message object
    user_message = {
        "role": "user", 
        "content": user_input
    }
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[system_message, user_message],
            api_key=OPENAI_API_KEY,
        )
        
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))