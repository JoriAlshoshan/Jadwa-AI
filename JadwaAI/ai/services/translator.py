# ai/services/translator.py
from ai.services.generative_ai import client  # نفس Client اللي عندك

def translate_text(text: str, target_lang: str) -> str:
    """
    Translate existing recommendations to target_lang ('ar' or 'en').
    """
    text = (text or "").strip()
    if not text:
        return ""

    target_lang = "ar" if str(target_lang).startswith("ar") else "en"

    system = (
        "You are a professional translator. "
        "Translate accurately, preserve formatting (bullet points, numbering, line breaks), "
        "and keep business/feasibility tone. Do not add new content."
    )

    user = f"Translate to {('Arabic' if target_lang=='ar' else 'English')}:\n\n{text}"

    resp = client.responses.create(
        model="gpt-5-mini",
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )

    return (resp.output_text or "").strip()
