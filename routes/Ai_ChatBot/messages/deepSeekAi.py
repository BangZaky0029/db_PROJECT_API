 
import requests
import json
from ..config.ai_config import API_KEY, API_URL, MODEL_API
from project_api.routes.Ai_ChatBot.core.message_generator import MessageGenerator


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
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openrouter.ai/",
            "X-Title": "AI Chat Bot",
            "User-Agent": "Mozilla/5.0"  # Added User-Agent
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
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500,
            "stream": False,
            "top_p": 0.9  # Added parameter for better response
        }

        print(f"Request URL: {API_URL}")
        print(f"Headers: {json.dumps(headers, indent=2)}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if not response.ok:
            return f"API Error: {response.status_code} - {response.text}"
        
        result = response.json()
        return result['choices'][0]['message']['content'].strip() if 'choices' in result else "No response generated"
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error: {str(e)}"

# Example usage
if __name__ == "__main__":
    prompt = "What is the meaning of life?"
    response = get_ai_response(prompt)
    print("AI Response:", response)