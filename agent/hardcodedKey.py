import openai
import os

# Use environment variable for API key - more secure
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Check if API key is available
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")


def ai_agent(user_input):
    """An AI agent that uses OpenAI to respond to user queries."""
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))