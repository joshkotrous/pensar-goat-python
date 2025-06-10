import openai
import os  # Pensar fix

# Pensar fix: Load API key from environment variable, not hard-coded.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_API_KEY is None:
    raise RuntimeError("OPENAI_API_KEY environment variable is not set. Please set it before running this script.")


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
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))