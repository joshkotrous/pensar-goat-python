import openai

OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def ai_agent(user_input):
    """A safer AI agent with reduced prompt injection risk."""
    system_prompt = (
        "You are an AI assistant. Answer the following user query as helpfully and safely as possible."
    )

    user_message = f"<user_input>\n{user_input}\n</user_input>"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        api_key=OPENAI_API_KEY,
    )

    return response["choices"][0]["message"]["content"]


while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))