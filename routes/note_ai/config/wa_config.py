# config/wa_config.py
# WhatsApp Configuration for Note AI Notifications

import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = "USiuXE5U1NjGKCTs5SLv"

# WhatsApp Numbers Configuration
NOMER_VINKA = "6285780307116"  # Vinka's WhatsApp number
NOMER_DESI = "6285215533928"  # Desi's WhatsApp number (formerly Mas David)
NOMER_DAVID = "6281288474727"  # David's WhatsApp number (formerly Mba Desi)
NOMER_IKBAL = "6285892622773"  # Ikbal's WhatsApp number
NOMER_UNTUNG = "6281288999768"  # Untung's WhatsApp number
NOMER_IMAM = "6281809742506"  # Imam's WhatsApp number

# User-Phone Mapping for @mentions
USER_PHONE_MAPPING = {
    "@vinka": NOMER_VINKA,
    "@desi": NOMER_DESI,
    "@david": NOMER_DAVID,
    "@ikbal": NOMER_IKBAL,
    "@untung": NOMER_UNTUNG,
    "@imam": NOMER_IMAM
}

# Admin-Platform Mapping
ADMIN_PLATFORMS = {
    "Vinka": {
        "platforms": ["WhatsApp"],
        "phone": NOMER_VINKA,
        "id": "1001"
    },
    "Desi": {
        "platforms": ["WhatsApp"],
        "phone": NOMER_DESI,
        "id": "1002"
    },
    "David": {
        "platforms": ["WhatsApp"],
        "phone": NOMER_DAVID,
        "id": "1003"
    },
    "Ikbal": {
        "platforms": ["WhatsApp"],
        "phone": NOMER_IKBAL,
        "id": "1004"
    },
    "Untung": {
        "platforms": ["WhatsApp"],
        "phone": NOMER_UNTUNG,
        "id": "1005"
    },
    "Imam": {
        "platforms": ["WhatsApp"],
        "phone": NOMER_IMAM,
        "id": "1006"
    }
}

# Supervisor Configuration (receives all summaries)
SUPERVISOR = {
    "phone": NOMER_VINKA,
    "platforms": ["WhatsApp", "Shopee", "TikTok", "Tokopedia", "Lazada"]
}

# Platform Categories
PLATFORMS = {
    "marketplace": ["Shopee", "TikTok", "Tokopedia", "Lazada"],
    "social": ["WhatsApp"]
}

# List of all numbers for batch processing
NOMER_WA = [NOMER_VINKA, NOMER_DESI, NOMER_DAVID, NOMER_IKBAL, NOMER_UNTUNG, NOMER_IMAM]

# Dictionary for easier identification
WA_RECIPIENTS = {
    "vinka": NOMER_VINKA,
    "desi": NOMER_DESI,
    "david": NOMER_DAVID,
    "ikbal": NOMER_IKBAL,
    "untung": NOMER_UNTUNG,
    "imam": NOMER_IMAM
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
        
        # Phone numbers
        self.vinka_phone = NOMER_VINKA
        self.desi_phone = NOMER_DESI
        self.david_phone = NOMER_DAVID
        self.ikbal_phone = NOMER_IKBAL
        self.untung_phone = NOMER_UNTUNG
        self.imam_phone = NOMER_IMAM
        
        # User mappings
        self.user_phone_mapping = USER_PHONE_MAPPING
        self.admin_platforms = ADMIN_PLATFORMS
        self.supervisor = SUPERVISOR
        self.platforms = PLATFORMS
        self.wa_recipients = WA_RECIPIENTS
        self.all_numbers = NOMER_WA
        
        logger.info("WhatsAppConfig initialized successfully")
    
    def get_user_phone(self, username: str) -> str:
        """Get phone number untuk user"""
        if not username.startswith('@'):
            username = f"@{username}"
        return self.user_phone_mapping.get(username.lower(), '')
    
    def is_valid_user(self, username: str) -> bool:
        """Check apakah user valid"""
        if not username.startswith('@'):
            username = f"@{username}"
        return username.lower() in self.user_phone_mapping