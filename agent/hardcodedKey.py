import openai

OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def ai_agent(user_input):
    """AI agent with prompt injection mitigation."""
    # Escape triple quotes to prevent prompt breaking
    safe_input = user_input.replace('"""', '\\"\\"\\"')

    prompt = (
        "You are an AI assistant. Answer the following user query, ensuring that your response is strictly based only on the user input delimited below:\n\n"
        "<START_OF_USER_INPUT>\n"
        f"{safe_input}\n"
        "<END_OF_USER_INPUT>\n\n"
        "AI:"
    )

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