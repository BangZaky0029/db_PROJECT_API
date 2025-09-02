import requests
import json
from ..config.ai_config import API_KEY, API_URL, MODEL_API
from ..core.message_generator import MessageGenerator


def get_ai_response(prompt):
    try:
        msg_gen = MessageGenerator()
        summary = msg_gen.generate_summary()
        
        ai_prompt = f"""Analisis dan berikan ringkasan dari data berikut dalam format yang mudah dibaca:

{summary}

Tolong berikan:
1. Ringkasan total pesanan pending
2. Highlight pesanan yang urgent (jika ada)
3. Rekomendasi prioritas pengerjaan
"""

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL_API,
            "messages": [
                {
                    "role": "system",
                    "content": "Anda adalah asisten AI yang membantu menjawab pertanyaan dalam Bahasa Indonesia dengan detail dan akurat."
                },
                {
                    "role": "user",
                    "content": ai_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 800,
            "top_p": 0.9,
            "stream": False
        }

        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

        if not response.ok:
            return f"API Error: {response.status_code} - {response.text}"

        result = response.json()
        return result['choices'][0]['message']['content'].strip()

    except Exception as e:
        return f"Error: {str(e)}"
