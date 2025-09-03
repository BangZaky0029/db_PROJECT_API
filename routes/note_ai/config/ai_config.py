# config/ai_config.py
# Konfigurasi AI untuk sistem notifikasi

import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = "TOGETHER_API_KEY=78a4b8df3c775ec51ef097bc6079db1e064fa821a3e9abe687022dff9736a435"
API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL_API = "meta-llama/Meta-Llama-3-70B-Instruct"

# AI Message Templates
AI_MESSAGE_TEMPLATES = {
    "note_notification": {
        "system_prompt": "You are a helpful assistant that formats note notifications for WhatsApp messages. Keep messages concise and professional.",
        "user_prompt_template": "Format this note information into a clear WhatsApp message:\n\nTitle: {title}\nContent: {content}\nCreated By: {created_by}\nDate: {created_at}\n\nMake it brief and informative."
    },
    "mention_alert": {
        "system_prompt": "You are a notification assistant. Create urgent but polite WhatsApp messages for @mentions.",
        "user_prompt_template": "Create a WhatsApp notification message for {mentioned_user} about this note:\n\nTitle: {title}\nContent: {content}\nCreated By: {created_by}\n\nMake it urgent but polite."
    }
}

# AI Request Configuration
AI_REQUEST_CONFIG = {
    "temperature": 0.7,
    "max_tokens": 200,
    "top_p": 0.9,
    "frequency_penalty": 0.1,
    "presence_penalty": 0.1
}

# Default Headers for AI API
DEFAULT_HEADERS = {
    "Authorization": f"Bearer {API_KEY.split('=')[1]}",
    "Content-Type": "application/json"
}

class AIConfig:
    """Konfigurasi AI untuk sistem notifikasi"""
    
    def __init__(self):
        # AI API Configuration
        self.API_KEY = API_KEY
        self.API_URL = API_URL
        self.MODEL_API = MODEL_API
        
        # Message templates
        self.AI_MESSAGE_TEMPLATES = AI_MESSAGE_TEMPLATES
        self.AI_REQUEST_CONFIG = AI_REQUEST_CONFIG
        self.DEFAULT_HEADERS = DEFAULT_HEADERS
        
        logger.info("AIConfig initialized successfully")
    
    def get_template(self, template_name: str) -> str:
        """Get AI message template"""
        return self.AI_MESSAGE_TEMPLATES.get(template_name, '')
    
    def get_request_config(self) -> dict:
        """Get AI request configuration"""
        return self.AI_REQUEST_CONFIG