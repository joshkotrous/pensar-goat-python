import openai
import os

# Retrieve API key from environment variables
def get_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set. Please set it to use this application.")
    return api_key


def ai_agent(user_input):
    """A more secure AI agent with environment-based API key."""
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
while True:
    try:
        user_query = input("Ask the AI: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        print(ai_agent(user_query))
    except ValueError as e:
        print(f"Error: {e}")
        break