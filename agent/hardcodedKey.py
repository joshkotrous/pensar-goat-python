import openai
import os

# Securely access the API key from environment variables
try:
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
except KeyError:
    raise ValueError(
        "OpenAI API key not found in environment variables. "
        "Please set the OPENAI_API_KEY environment variable. "
        "You can do this by running:\n"
        "  export OPENAI_API_KEY='your-api-key' (Linux/macOS)\n"
        "  set OPENAI_API_KEY=your-api-key (Windows Command Prompt)\n"
        "  $env:OPENAI_API_KEY='your-api-key' (Windows PowerShell)"
    )


def ai_agent(user_input):
    """An AI agent that securely handles API credentials."""
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=OPENAI_API_KEY,  # Now using securely obtained key
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))