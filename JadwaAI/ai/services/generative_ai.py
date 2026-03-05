# import os
# from dotenv import load_dotenv
# from openai import OpenAI

# load_dotenv() 

# client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY")  
# )

# def generate_recommendations(prompt: str) -> str:
#     response = client.responses.create(
#         model="gpt-5-mini",
#         input=prompt
#     )
#     return response.output_text

# ai/services/generative_ai.py
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_recommendations(prompt: str, timeout: int = 20) -> str:
    try:
        resp = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            input=prompt,
            timeout=timeout,  
        )
        return (resp.output_text or "").strip()
    except Exception as e:
        return f"Failed to generate recommendations: {e}"