# services/whatsapp_service.py
# WhatsApp Notification Service for Note AI

import sys
import os
import requests
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional

# Add parent directory to path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from config.wa_config import (
    API_KEY,
    FONTTE_API_URL,
    FONTTE_HEADERS,
    USER_PHONE_MAPPING,
    WA_RECIPIENTS,
    WhatsAppConfig
)
from config.ai_config import (
    AIConfig
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppNotificationService:
    """Service untuk mengirim notifikasi WhatsApp otomatis"""
    
    def __init__(self):
        self.config = WhatsAppConfig()
        self.api_url = self.config.api_url
        self.headers = self.config.headers
        self.user_mapping = self.config.user_phone_mapping
    
    def send_message(self, phone_number, message):
        """
        Mengirim pesan WhatsApp ke nomor tertentu
        
        Args:
            phone_number (str): Nomor WhatsApp tujuan
            message (str): Pesan yang akan dikirim
            
        Returns:
            dict: Response dari API Fonnte
        """
        try:
            payload = {
                "target": phone_number,
                "message": message,
                "countryCode": "62"
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                logger.info(f"WhatsApp message sent successfully to {phone_number}")
                return {
                    "status": "success",
                    "message": "Message sent successfully",
                    "response": response.json()
                }
            else:
                logger.error(f"Failed to send WhatsApp message: {response.text}")
                return {
                    "status": "error",
                    "message": f"Failed to send message: {response.text}",
                    "response": None
                }
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {
                "status": "error",
                "message": f"Error sending message: {str(e)}",
                "response": None
            }
    
    def send_note_notification(self, note_data, mentioned_users=None):
        """
        Mengirim notifikasi note ke user yang di-mention
        
        Args:
            note_data (dict): Data note yang berisi title, content, created_by, dll
            mentioned_users (list): List user yang di-mention (contoh: ['@imam'])
            
        Returns:
            dict: Status pengiriman pesan
        """
        try:
            if not mentioned_users:
                return {
                    "status": "info",
                    "message": "No users mentioned, no notification sent"
                }
            
            results = []
            
            for user in mentioned_users:
                if user.lower() in self.user_mapping:
                    phone_number = self.user_mapping[user.lower()]
                    
                    # Format pesan notifikasi
                    message = self._format_note_message(note_data, user)
                    
                    # Kirim pesan
                    result = self.send_message(phone_number, message)
                    result['user'] = user
                    result['phone'] = phone_number
                    results.append(result)
                    
                    logger.info(f"Notification sent to {user} ({phone_number})")
                else:
                    logger.warning(f"User {user} not found in mapping")
                    results.append({
                        "status": "error",
                        "message": f"User {user} not found in mapping",
                        "user": user,
                        "phone": None
                    })
            
            # Check if any notification was successful
            success_count = sum(1 for r in results if r.get('status') == 'success')
            
            return {
                "success": success_count > 0,
                "status": "success" if success_count > 0 else "error",
                "message": f"Notifications processed for {len(results)} users",
                "results": results,
                "notifications_sent": success_count,
                "notifications_failed": len(results) - success_count
            }
            
        except Exception as e:
            logger.error(f"Error sending note notifications: {str(e)}")
            return {
                "success": False,
                "status": "error",
                "message": f"Error sending notifications: {str(e)}",
                "error": str(e),
                "results": [],
                "notifications_sent": 0,
                "notifications_failed": 1
            }
    
    def _format_note_message(self, note_data, mentioned_user):
        """
        Format pesan notifikasi note
        
        Args:
            note_data (dict): Data note
            mentioned_user (str): User yang di-mention
            
        Returns:
            str: Pesan yang sudah diformat
        """
        try:
            # Format tanggal
            created_at = note_data.get('created_at', datetime.now())
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            # Format pesan
            message = f"🔔 *NOTIFIKASI NOTE* \n"
            message += f"👤 From: {note_data.get('created_by', 'N/A')}\n"
            message += f"Halo {mentioned_user.replace('@', '').title()},\n"
            message += f"Anda di-mention dalam note baru:\n"
            message += f"📝 Judul: {note_data.get('note_title', 'N/A')}\n"
            message += f"🆔 ID Input: {note_data.get('id_input', 'N/A')}\n"
            message += f"📊 Sumber: {note_data.get('table_source', 'N/A')}\n\n"
            message += f"💬 Pesan: \n"
            message += f"{note_data.get('note_content', 'N/A')}\n\n"
            
            return message
            
        except Exception as e:
            logger.error(f"Error formatting message: {str(e)}")
            return f"Halo {mentioned_user.replace('@', '').title()},\n\nAnda di-mention dalam note baru:\n\n📝 {note_data.get('note_title', 'N/A')}\n\n🆔 ID Input: {note_data.get('id_input', 'N/A')}\n📊 Sumber: {note_data.get('table_source', 'N/A')}\n\n{note_data.get('note_content', 'N/A')}\n\n👤 From: {note_data.get('created_by', 'N/A')}"
    
    def get_user_phone(self, username):
        """
        Mendapatkan nomor telepon user berdasarkan username
        
        Args:
            username (str): Username (contoh: '@imam' atau 'imam')
            
        Returns:
            str: Nomor telepon atau None jika tidak ditemukan
        """
        # Normalize username
        if not username.startswith('@'):
            username = f"@{username}"
        
        return self.user_mapping.get(username.lower())
    
    def is_user_exists(self, username):
        """
        Cek apakah user ada dalam mapping
        
        Args:
            username (str): Username yang akan dicek
            
        Returns:
            bool: True jika user ada, False jika tidak
        """
        if not username.startswith('@'):
            username = f"@{username}"
        
        return username.lower() in self.user_mapping

# Instance global untuk digunakan di module lain
whatsapp_service = WhatsAppNotificationService()