import os
import openai

def get_openai_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set. Exiting.")
        exit(1)
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
        api_key=get_openai_api_key(),
    )

    return response["choices"][0]["message"]["content"]


while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))