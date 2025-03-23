import openai
import os

# Get API key from environment variable
# To set the environment variable:
# - On Linux/Mac: export OPENAI_API_KEY="your-api-key"
# - On Windows: set OPENAI_API_KEY=your-api-key


def ai_agent(user_input):
    """An AI agent that securely handles API keys."""
    # Check if the API key is available
    if "OPENAI_API_KEY" not in os.environ:
        return "Error: OPENAI_API_KEY environment variable is not set."

    prompt = f"""
    You are an AI assistant. Answer the following user query:
    
    User: {user_input}
    AI:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        # Use API key from environment variable
        api_key=os.environ["OPENAI_API_KEY"],
    )

    return response["choices"][0]["message"]["content"]


# Example usage
while True:
    user_query = input("Ask the AI: ")
    if user_query.lower() in ["exit", "quit"]:
        break
    print(ai_agent(user_query))