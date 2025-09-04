# test_notification.py
# Test endpoint untuk sistem notifikasi WhatsApp

from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import notification handler
try:
    from core.note_notification_handler import notification_handler
    NOTIFICATION_AVAILABLE = True
except ImportError as e:
    NOTIFICATION_AVAILABLE = False
    notification_handler = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
test_notification_bp = Blueprint('test_notification', __name__)

@test_notification_bp.route('/api/test/notification', methods=['POST'])
def test_notification():
    """
    Test endpoint untuk sistem notifikasi WhatsApp
    
    Body (optional):
    {
        "note_title": "@imam Test notification",
        "note_content": "Test content",
        "created_by": "Test User"
    }
    """
    try:
        if not NOTIFICATION_AVAILABLE:
            return jsonify({
                'status': 'error',
                'message': 'Notification system not available',
                'available': False
            }), 500
        
        # Get test data dari request atau gunakan default
        data = request.get_json() if request.is_json else {}
        
        test_note_data = {
            'id_input': f'TEST-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'note_title': data.get('note_title', '@imam Test Notification System'),
            'note_content': data.get('note_content', 'Ini adalah test notifikasi sistem WhatsApp. Mohon konfirmasi jika pesan ini diterima.'),
            'created_by': data.get('created_by', 'System Test'),
            'table_source': 'table_design',
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(f"Starting notification test with data: {test_note_data['note_title']}")
        
        # Test notification system
        result = notification_handler.test_notification_system(test_note_data)
        
        # Format response
        response = {
            'status': 'success' if result.get('success') else 'error',
            'message': result.get('message', 'Test completed'),
            'test_data': test_note_data,
            'result': result,
            'timestamp': datetime.now().isoformat()
        }
        
        status_code = 200 if result.get('success') else 400
        
        logger.info(f"Notification test completed: {result.get('message')}")
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Error in notification test: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Test failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@test_notification_bp.route('/api/test/notification/status', methods=['GET'])
def get_notification_status():
    """
    Get status sistem notifikasi
    """
    try:
        if not NOTIFICATION_AVAILABLE:
            return jsonify({
                'status': 'error',
                'message': 'Notification system not available',
                'available': False,
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get system status
        status = notification_handler.get_system_status()
        
        return jsonify({
            'status': 'success',
            'message': 'System status retrieved',
            'system_status': status,
            'available': True,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting notification status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to get status: {str(e)}',
            'available': NOTIFICATION_AVAILABLE,
            'timestamp': datetime.now().isoformat()
        }), 500

@test_notification_bp.route('/api/test/notification/mentions', methods=['POST'])
def test_mention_parsing():
    """
    Test mention parsing functionality
    
    Body:
    {
        "text": "@imam @vinka test mention parsing"
    }
    """
    try:
        if not NOTIFICATION_AVAILABLE:
            return jsonify({
                'status': 'error',
                'message': 'Notification system not available',
                'available': False
            }), 500
        
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Text field is required'
            }), 400
        
        text = data['text']
        
        # Test mention parsing
        mentions = notification_handler.mention_parser.extract_mentions(text)
        valid_mentions = [m for m in mentions if notification_handler.mention_parser.is_valid_mention(m)]
        
        # Get supported users
        supported_users = list(notification_handler.wa_config.user_phone_mapping.keys())
        
        result = {
            'input_text': text,
            'extracted_mentions': mentions,
            'valid_mentions': valid_mentions,
            'supported_users': supported_users,
            'mention_count': len(valid_mentions)
        }
        
        return jsonify({
            'status': 'success',
            'message': 'Mention parsing completed',
            'result': result,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in mention parsing test: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Mention parsing test failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@test_notification_bp.route('/api/test/notification/format', methods=['POST'])
def test_message_formatting():
    """
    Test message formatting functionality
    
    Body:
    {
        "note_data": {
            "note_title": "Test Note",
            "note_content": "Test content",
            "created_by": "Test User"
        },
        "mentioned_user": "@imam",
        "template_type": "note_mention"
    }
    """
    try:
        if not NOTIFICATION_AVAILABLE:
            return jsonify({
                'status': 'error',
                'message': 'Notification system not available',
                'available': False
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Request body is required'
            }), 400
        
        # Default test data
        note_data = data.get('note_data', {
            'id_input': 'TEST-001',
            'note_title': 'Test Notification',
            'note_content': 'This is a test message formatting',
            'created_by': 'Test User',
            'table_source': 'table_design',
            'created_at': datetime.now().isoformat()
        })
        
        mentioned_user = data.get('mentioned_user', '@imam')
        template_type = data.get('template_type', 'note_mention')
        
        # Test message formatting
        formatted_message = notification_handler.message_formatter.format_note_notification(
            note_data, mentioned_user, template_type
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Message formatting completed',
            'input_data': {
                'note_data': note_data,
                'mentioned_user': mentioned_user,
                'template_type': template_type
            },
            'formatted_message': formatted_message,
            'message_length': len(formatted_message),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in message formatting test: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Message formatting test failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

# Health check endpoint
@test_notification_bp.route('/api/test/notification/health', methods=['GET'])
def health_check():
    """
    Health check untuk notification system
    """
    try:
        health_status = {
            'notification_system': 'available' if NOTIFICATION_AVAILABLE else 'unavailable',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        if NOTIFICATION_AVAILABLE:
            # Test basic functionality
            try:
                status = notification_handler.get_system_status()
                health_status['system_status'] = status.get('system_status', 'unknown')
                health_status['components'] = status.get('components', {})
            except Exception as e:
                health_status['system_status'] = 'error'
                health_status['error'] = str(e)
        
        return jsonify({
            'status': 'success',
            'message': 'Health check completed',
            'health': health_status
        }), 200
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Health check failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500