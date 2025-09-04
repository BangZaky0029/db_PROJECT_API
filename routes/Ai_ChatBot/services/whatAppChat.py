 
from flask import Blueprint, jsonify, request
import threading
import time
import logging
import json
from ..config.core.message_generator import MessageGenerator
from ..messages.message_service import send_whatsapp_message
from ..config.wa_config import NOMER_1, NOMER_2, NOMER_3, NOMER_4
from ..messages.deepSeekAi import get_ai_response
from .scheduler import start_scheduler

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

whatsapp_bp = Blueprint('whatsapp', __name__)

@whatsapp_bp.route("/test-ai", methods=["POST"])
def test_ai():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        msg_gen = MessageGenerator()
        summary = msg_gen.generate_summary()
        
        ai_prompt = f"""Analisis dan berikan ringkasan dari data berikut:

{summary}

Tolong berikan:
1. Total pesanan pending per deadline
2. Highlight pesanan urgent (jika ada)
3. Saran prioritas pengerjaan
"""
        ai_response = get_ai_response(ai_prompt)
        
        return jsonify({
            "status": "success",
            "prompt": prompt,
            "response": ai_response,
            "raw_summary": summary
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@whatsapp_bp.route("/whatsapp/send-messages", methods=['POST'])
def send_messages():
    try:
        logger.debug("Starting message generation process")
        msg_gen = MessageGenerator()
        results = {}
        
        # Validate admin numbers
        if not all([NOMER_1, NOMER_2, NOMER_3, NOMER_4]):
            raise ValueError("Admin phone numbers not properly configured")
            
        admins = [
            {"phone": NOMER_1, "id_admin": "1001"},
            {"phone": NOMER_2, "id_admin": "1002"},
            {"phone": NOMER_3, "id_admin": "1003"},
            {"phone": NOMER_4, "id_admin": "supervisor"}
        ]
        
        logger.debug(f"Processing admins: {json.dumps(admins, cls=JSONEncoder)}")
        
        for admin in admins:
            try:
                logger.debug(f"Processing admin data: {json.dumps(admin, cls=JSONEncoder)}")
                
                if not admin.get("phone") or not admin.get("id_admin"):
                    logger.warning(f"Incomplete admin data: {json.dumps(admin, cls=JSONEncoder)}")
                    continue
                    
                message = msg_gen.generate_message(id_admin=str(admin["id_admin"]))
                logger.debug(f"Generated message for {admin['id_admin']}: {message[:100]}...")
                
                if message:
                    success = send_whatsapp_message(admin['phone'], message)
                    result = {
                        "status": "Success" if success else "Failed",
                        "id_admin": admin["id_admin"],
                        "message_length": len(message)
                    }
                    logger.debug(f"Message result: {json.dumps(result, cls=JSONEncoder)}")
                    results[admin['phone']] = result
                
                time.sleep(1)
                
            except Exception as e:
                error_data = {
                    "status": "Error",
                    "error": str(e),
                    "id_admin": admin.get("id_admin", "Unknown")
                }
                logger.exception(f"Admin processing error: {json.dumps(error_data, cls=JSONEncoder)}")
                results[admin['phone']] = error_data
        
        response_data = {
            "status": "success" if results else "warning",
            "results": results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        logger.debug(f"Final response: {json.dumps(response_data, cls=JSONEncoder)}")
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            "status": "error",
            "message": str(e),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        logger.exception(f"Global error: {json.dumps(error_response, cls=JSONEncoder)}")
        return jsonify(error_response), 500

def init_scheduler():
    """Initialize the scheduler in a separate thread"""
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()


@whatsapp_bp.route("/test-ai-response", methods=["GET", "POST"])
def test_ai_endpoint():
    """Test endpoint for AI response"""
    try:
        from ..messages.message_service import test_ai_response
        
        if request.method == "POST":
            data = request.get_json() or {}
            custom_prompt = data.get('prompt')
            result = test_ai_response(custom_prompt)
        else:
            # GET request - use default prompt
            result = test_ai_response()
            
        return jsonify(result)
    except Exception as e:
        logger.exception("Error in test AI endpoint")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@whatsapp_bp.route("/test-database", methods=["GET"])
def test_database():
    """Test database connection and data"""
    try:
        from ..services.database_service import DatabaseService
        
        db_service = DatabaseService()
        connection_test = db_service.test_connection()
        
        # Also get pending orders
        pending_orders = db_service.get_pending_orders()
        
        return jsonify({
            "status": "success",
            "connection_test": connection_test,
            "pending_orders_count": len(pending_orders) if pending_orders else 0,
            "pending_orders_sample": pending_orders[:3] if pending_orders and len(pending_orders) > 0 else []
        })
    except Exception as e:
        logger.exception("Error testing database")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
