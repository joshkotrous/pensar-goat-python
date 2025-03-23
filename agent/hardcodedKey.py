import openai
import os

# Use environment variables for sensitive data
try:
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
except KeyError:
    raise RuntimeError(
        "Please set the OPENAI_API_KEY environment variable. "
        "You can get your API key from the OpenAI dashboard."
    )


def ai_agent(user_input):
    """An AI agent that securely handles API authentication."""
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