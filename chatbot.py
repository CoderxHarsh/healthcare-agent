# import google.generativeai as genai
from langchain_groq import ChatGroq
# Source - https://stackoverflow.com/a/68200726
# Posted by Martin Tovmassian, modified by community. See post 'Timeline' for change history
# Retrieved 2026-04-04, License - CC BY-SA 4.0

import os                                                                                                                                                                                                          
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
load_dotenv(Path("./.env"))

# Load variables from .env before reading GROK_API_KEY.


api_key = os.getenv("GROK_API_KEY")
if not api_key:
    raise RuntimeError(
        "Missing GROK_API_KEY. Add it to your .env file or environment variables."
    )

# genai.configure(api_key=api_key)

# model = ChatGroq(model="grok-2", temperature=0.5)
model = ChatGroq(
    model = "openai/gpt-oss-20b",
    api_key = api_key,
    temperature =0.7,
    max_tokens = 2048
)
def get_response(user_input):
    prompt = f"""
    You are a helpful health assistant.

    Answer clearly and safely.
    Try to be concise and supportive.
    Don't give long explanations.`
    Avoid giving dangerous medical advice.

    User: {user_input}
    """

    response = model.invoke(prompt)
    return response.text