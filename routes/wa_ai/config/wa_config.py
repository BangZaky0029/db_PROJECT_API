# config/wa_config.py
# WhatsApp Configuration for Note AI Notifications

import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = "USiuXE5U1NjGKCTs5SLv"

# List of Penjahit numbers for batch processing
NOMER_PENJAHIT = [
    "+62 882-9204-1656",  # Mas Ari
    "+62 814-6049-9063",  # Mas Uu
    "+62 882-1049-9472",  # Mas Egeng
    "+62 888-1620-145",   # Mas Saep
    "+62 813-8332-2396",  # Pak Maman
    "+62 877-8262-7176",  # Pak Kamto
    "+62 831-3526-2394",  # Mas Gugun
    "+62 819-9577-0190"   # Nomor tambahan
]

# List of Press numbers for batch processing
NOMER_PRESS = [
    "+62 895-7115-46622",  # Zidan
    "+62 856-4224-7492"    # Jujun
]

# List of Reject numbers for batch processing
NOMER_REJECT = [
    "+62 838-0437-8190"    # Teddy
]


# Dictionary for Penjahit class
PENJAHIT_RECIPIENTS = {
    "Mas_Ari": "+62 882-9204-1656",
    "Mas_Uu": "+62 814-6049-9063",
    "Mas_Egeng": "+62 882-1049-9472",
    "Mas_Saep": "+62 888-1620-145",
    "Pak_Maman": "+62 813-8332-2396",
    "Pak_Kamto": "+62 877-8262-7176",
    "Mas_Gugun": "+62 831-3526-2394"
}

# Dictionary for Press class
PRESS_RECIPIENTS = {
    "Zidan": "+62 895-7115-46622",
    "Jujun": "+62 856-4224-7492"
}

# Dictionary for Reject class
REJECT_RECIPIENTS = {
    "Teddy": "+62 838-0437-8190"
}

# Fonnte API Configuration
FONTTE_API_URL = "https://api.fonnte.com/send"
FONTTE_HEADERS = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

class WhatsAppConfig:
    """Konfigurasi WhatsApp untuk sistem notifikasi"""
    
    def __init__(self):
        # WhatsApp API Configuration
        self.api_key = API_KEY
        self.api_url = FONTTE_API_URL
        self.headers = FONTTE_HEADERS
        
        # User mappings
        self.penjahit_recipients = PENJAHIT_RECIPIENTS
        self.press_recipients = PRESS_RECIPIENTS
        self.reject_recipients = REJECT_RECIPIENTS
        self.penjahit_numbers = NOMER_PENJAHIT
        self.press_numbers = NOMER_PRESS
        self.reject_numbers = NOMER_REJECT
        
        # Phone numbers - Penjahit
        self.mas_ari_phone = PENJAHIT_RECIPIENTS["Mas_Ari"]
        self.mas_uu_phone = PENJAHIT_RECIPIENTS["Mas_Uu"]
        self.mas_egeng_phone = PENJAHIT_RECIPIENTS["Mas_Egeng"]
        self.mas_saep_phone = PENJAHIT_RECIPIENTS["Mas_Saep"]
        self.pak_maman_phone = PENJAHIT_RECIPIENTS["Pak_Maman"]
        self.pak_kamto_phone = PENJAHIT_RECIPIENTS["Pak_Kamto"]
        self.mas_gugun_phone = PENJAHIT_RECIPIENTS["Mas_Gugun"]
        
        # Phone numbers - Press
        self.zidan_phone = PRESS_RECIPIENTS["Zidan"]
        self.jujun_phone = PRESS_RECIPIENTS["Jujun"]
        
        # Phone numbers - Reject
        self.teddy_phone = REJECT_RECIPIENTS["Teddy"]
        
        logger.info("WhatsAppConfig initialized successfully")
   