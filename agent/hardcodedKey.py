import openai
import os

# Securely retrieve API key from environment variables
try:
    OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
    if not OPENAI_API_KEY:
        raise KeyError("OPENAI_API_KEY is empty")
except KeyError:
    print("""
Error: OPENAI_API_KEY environment variable is not set or is empty.

To set the environment variable:

1. For Windows:
   set OPENAI_API_KEY=your_api_key_here

2. For macOS/Linux:
   export OPENAI_API_KEY=your_api_key_here

Please set the API key and try again.
""")
    OPENAI_API_KEY = None


def ai_agent(user_input):
    """An AI agent with prompt injection risk."""
    if OPENAI_API_KEY is None:
        return "Error: API key is not available. Please set the OPENAI_API_KEY environment variable."
    
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            api_key=OPENAI_API_KEY,
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        # Avoid including the API key in error messages
        error_message = str(e)
        if OPENAI_API_KEY in error_message:
            error_message = error_message.replace(OPENAI_API_KEY, "[API_KEY_REDACTED]")
        return f"An error occurred when calling the OpenAI API: {error_message}"


# Example usage with proper error handling
if __name__ == "__main__":
    while True:
        user_query = input("Ask the AI: ")
        if user_query.lower() in ["exit", "quit"]:
            break
        print(ai_agent(user_query))