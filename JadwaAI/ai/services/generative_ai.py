import os
import time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def generate_recommendations(prompt: str, timeout: int | None = None) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OPENAI_API_KEY is missing."

    client = OpenAI(api_key=api_key)

    if timeout is None:
        timeout = int(os.getenv("OPENAI_TIMEOUT", "60"))

    last_err = None
    for attempt in range(2):  
        try:
            resp = client.responses.create(
                model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
                input=prompt,
                timeout=timeout,
            )
            return (resp.output_text or "").strip()

        except Exception as e:
            last_err = e
            if attempt == 0:
                time.sleep(1.5)
                continue

    return f"Failed to generate recommendations: {last_err}"