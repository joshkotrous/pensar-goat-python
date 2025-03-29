import openai
import os

# Secure API key handling using environment variables
# Set your API key as an environment variable named OPENAI_API_KEY


def ai_agent(user_input):
    """A vulnerable AI agent with prompt injection risk."""
    # Check if API key is available in environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )
    
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=api_key,  # Using environment variable
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    try:
        print(ai_agent(user_query))
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set your OpenAI API key as an environment variable and try again.")
        break