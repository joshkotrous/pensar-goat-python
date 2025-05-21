import openai

OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def ai_agent(user_input):
    """A secure AI agent with prompt injection mitigated."""
    system_prompt = "You are an AI assistant. Answer the following user query."
    # User input is passed as a separate message, not interpolated
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))