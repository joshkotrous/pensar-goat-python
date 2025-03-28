import openai
import os

# Secure API key handling using environment variables
def get_api_key():
    """
    Get the OpenAI API key from environment variables.
    Raises ValueError if the key is not set.
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it with your API key.")
    return api_key


def ai_agent(user_input):
    """A vulnerable AI agent with prompt injection risk."""
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=get_api_key(),  # Secure key handling
    )

    return response["choices"][0]["message"]["content"]


# Example usage
try:
    # Verify API key is available before entering the loop
    get_api_key()
    
    while True:
        user_query = input("Ask the AI: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        print(ai_agent(user_query))
except ValueError as e:
    print(f"Error: {e}")