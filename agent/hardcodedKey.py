import openai
import os

# Secure API key handling using environment variables
def get_api_key():
    """Get the API key from environment variables."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set the environment variable with your API key:")
        print("  export OPENAI_API_KEY='your-api-key'  # for Unix/Linux/MacOS")
        print("  set OPENAI_API_KEY=your-api-key  # for Windows Command Prompt")
        print("  $env:OPENAI_API_KEY='your-api-key'  # for Windows PowerShell")
    return api_key


def ai_agent(user_input):
    """A more secure AI agent with environment variable for API key."""
    api_key = get_api_key()
    
    if not api_key:
        return "Error: OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable."
    
    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        api_key=api_key,  # Now using environment variable
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))