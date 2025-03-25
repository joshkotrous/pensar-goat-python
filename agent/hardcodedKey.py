import openai
import os  # Added to access environment variables

# Secure API key handling using environment variables
# The API key should be set in the environment variable OPENAI_API_KEY


def ai_agent(user_input):
    """An AI agent that generates responses to user queries."""
    # Get the API key from environment variables
    api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        return "Error: OpenAI API key not found in environment variables. Please set the OPENAI_API_KEY environment variable."
    
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
    print(ai_agent(user_query))