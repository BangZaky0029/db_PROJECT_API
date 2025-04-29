API_KEY = "USiuXE5U1NjGKCTs5SLv"

# WhatsApp Numbers Configuration
NOMER_1 = "628111803588"  # ADMIN_LILIS
NOMER_2 = "6281288999768"  # ADMIN_INA
NOMER_3 = "6281283787676"  # ADMIN_INDY
NOMER_4 = "6281808486767"  # Mba Diah

# Admin-Platform Mapping
ADMIN_PLATFORMS = {
    "Lilis": {
        "platforms": ["WhatsApp"],
        "phone": NOMER_1,
        "id": "1001"
    },
    "Ina": {
        "platforms": ["WhatsApp"],
        "phone": NOMER_2,
        "id": "1002"
    },
    "Indy": {
        "platforms": ["WhatsApp"],
        "phone": NOMER_3,
        "id": "1003"
    }
}

# Supervisor Configuration (receives all summaries)
SUPERVISOR = {
    "phone": NOMER_4,
    "platforms": ["WhatsApp", "Shopee", "TikTok", "Tokopedia", "Lazada"]
}

# Platform Categories
PLATFORMS = {
    "marketplace": ["Shopee", "TikTok", "Tokopedia", "Lazada"],
    "social": ["WhatsApp"]
}

# List of all numbers for batch processing
NOMER_WA = [NOMER_1, NOMER_2, NOMER_3, NOMER_4]

# Dictionary for easier identification
WA_RECIPIENTS = {
    "admin_lilis": NOMER_1,
    "admin_ina": NOMER_2,
    "admin_indy": NOMER_3,
    "supervisor": NOMER_4
}

# Platform responsibility mapping
PLATFORM_ADMINS = {
    "WhatsApp": ["Lilis", "Ina", "Indy"],
    "Shopee": ["supervisor"],
    "TikTok": ["supervisor"],
    "Tokopedia": ["supervisor"],
    "Lazada": ["supervisor"]
}