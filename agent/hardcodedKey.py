import openai
import os

# API key should be set as an environment variable named OPENAI_API_KEY
# For example: export OPENAI_API_KEY="your-api-key-here"


def ai_agent(user_input):
    """A vulnerable AI agent with prompt injection risk."""
    # Check if API key is available in environment
    if "OPENAI_API_KEY" not in os.environ:
        return "Error: OPENAI_API_KEY environment variable not set. Please set it with your OpenAI API key."
    
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=os.environ["OPENAI_API_KEY"],  # Secure key handling from environment
    )

    return response["choices"][0]["message"]["content"]


# Example vulnerable usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))