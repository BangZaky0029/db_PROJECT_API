 
import requests
import logging
from datetime import datetime
from flask import jsonify, request
from ..config.wa_config import (
    API_KEY, NOMER_1, NOMER_2, NOMER_3, NOMER_4,
    ADMIN_PLATFORMS, SUPERVISOR, PLATFORM_ADMINS
)

from ..config.core.message_generator import MessageGenerator
from ..messages.deepSeekAi import get_ai_response

logger = logging.getLogger(__name__)

def create_messages():
    """Create messages for each admin"""
    try:
        msg_gen = MessageGenerator()
        messages = {}
        
        # Get messages for regular admins
        for admin_name, admin_info in ADMIN_PLATFORMS.items():
            admin_message = msg_gen.generate_message(id_admin=admin_info['id'])
            messages[admin_info['phone']] = admin_message
            
        # Get summary message for supervisor
        supervisor_message = msg_gen.generate_supervisor_message()
        messages[SUPERVISOR['phone']] = supervisor_message
        
        return messages
    except Exception as e:
        logger.error(f"Error in create_messages: {str(e)}")
        return {}

def send_whatsapp_message(phone, message):
    """Send WhatsApp message using Fonnte API"""
    if not message:
        print(f"Empty message for {phone}")
        return False

    url = "https://api.fonnte.com/send"
    payload = {
        "target": phone,
        "message": message
    }
    headers = {
        "Authorization": API_KEY
    }

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        if response.status_code != 200:
            print(f"Error sending message: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Failed to send message: {str(e)}")
        return False

def send_scheduled_message():
    """Send scheduled messages to all admins"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        messages = create_messages()
        results = []
        
        if not messages:
            return jsonify({
                "status": "info",
                "message": "No pending orders to report",
                "timestamp": current_time
            })
            
        # Send messages to each admin
        for phone, message in messages.items():
            success = send_whatsapp_message(phone, message)
            results.append({
                "phone": phone,
                "success": success,
                "timestamp": current_time
            })
            print(f"[{current_time}] {'Success' if success else 'Failed'} sending to {phone}")
                
        return jsonify({
            "status": "success",
            "results": results,
            "timestamp": current_time
        })
                
    except Exception as e:
        print(f"[{current_time}] Error in send_scheduled_message: {e}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": current_time
        }), 500

# Add route handler
def handle_send_messages():
    """Handle POST request for sending messages"""
    if request.method == 'POST':
        return send_scheduled_message()
    return jsonify({"error": "Method not allowed"}), 405


def test_ai_response(prompt=None):
    """Test AI response with custom or default prompt"""
    try:
        if not prompt:
            msg_gen = MessageGenerator()
            all_orders = msg_gen.generate_message()
            
            prompt = f"""Analisis dan berikan ringkasan dari data berikut:

{all_orders}

Tolong berikan:
1. Total pesanan pending per deadline
2. Highlight pesanan urgent (jika ada)
3. Saran prioritas pengerjaan
"""
        
        ai_response = get_ai_response(prompt)
        return {
            "status": "success",
            "prompt": prompt,
            "response": ai_response
        }
    except Exception as e:
        logger.error(f"Error testing AI: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }