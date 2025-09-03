from flask import Blueprint, request, jsonify
import mysql.connector
import logging
from datetime import datetime
from db import get_db_connection

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import WhatsApp notification system
try:
    import sys
    import os
    # Add note_ai path to sys.path
    note_ai_path = os.path.join(os.path.dirname(__file__), 'note_ai')
    if note_ai_path not in sys.path:
        sys.path.insert(0, note_ai_path)
    
    from core.note_notification_handler import notification_handler
    NOTIFICATION_ENABLED = True
    logger.info("WhatsApp notification system loaded successfully")
except ImportError as e:
    NOTIFICATION_ENABLED = False
    logger.warning(f"WhatsApp notification system not available: {str(e)}")

# Create Blueprint
note_bp = Blueprint('note_operations', __name__)

# User PIN mapping
USER_PINS = {
    'Mba Desi': '2389',
    'Vinka': '1507',
    'Ikbal': '2380',
    'Mas David': '9187',
    'Untung': '7435',
    'Imam': '4985'
}

# Database connection imported from db.py

# Database connection imported from db.py

# CREATE - Tambah note baru
@note_bp.route('/api/notes', methods=['POST'])
def create_note():
    try:
        data = request.get_json()
        
        # Validasi input
        required_fields = ['id_input', 'table_source', 'note_title', 'note_content', 'created_by']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'status': 'error',
                    'message': f'Field {field} is required'
                }), 400
        
        # Validasi table_source
        valid_sources = ['table_design', 'table_produksi', 'table_pesanan']
        if data['table_source'] not in valid_sources:
            return jsonify({
                'status': 'error',
                'message': 'Invalid table_source. Must be one of: ' + ', '.join(valid_sources)
            }), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'message': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Insert note
        insert_query = """
            INSERT INTO table_note (id_input, table_source, note_title, note_content, created_by)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_query, (
            data['id_input'],
            data['table_source'],
            data['note_title'],
            data['note_content'],
            data['created_by']
        ))
        
        note_id = cursor.lastrowid
        conn.commit()
        
        logger.info(f"Note created successfully with ID: {note_id}")
        
        # Prepare note data untuk notification system
        note_data = {
            'id_input': data['id_input'],
            'table_source': data['table_source'],
            'note_title': data['note_title'],
            'note_content': data['note_content'],
            'created_by': data['created_by'],
            'note_id': note_id,
            'created_at': datetime.now().isoformat()
        }
        
        # Process WhatsApp notifications jika ada mention
        notification_result = None
        logger.info(f"NOTIFICATION_ENABLED status: {NOTIFICATION_ENABLED}")
        logger.info(f"Note data for notification: {note_data}")
        
        if NOTIFICATION_ENABLED:
            try:
                logger.info("Starting notification processing...")
                notification_result = notification_handler.process_note_creation(note_data)
                logger.info(f"Notification processing completed: {notification_result.get('message', 'No details')}")
                logger.info(f"Full notification result: {notification_result}")
            except Exception as e:
                logger.error(f"Error processing notifications: {str(e)}")
                notification_result = {
                    'success': False,
                    'error': str(e),
                    'message': 'Notification processing failed'
                }
        else:
            logger.warning("Notification system is disabled or not available")
        
        # Prepare response
        response_data = {
            'status': 'success',
            'message': 'Note created successfully',
            'note_id': note_id
        }
        
        # Add notification info jika ada
        if notification_result:
            response_data['notification'] = {
                'enabled': NOTIFICATION_ENABLED,
                'mentions_processed': notification_result.get('mentions_processed', 0),
                'notifications_sent': notification_result.get('notifications_sent', 0),
                'success': notification_result.get('success', False)
            }
            
            # Add notification details jika berhasil
            if notification_result.get('success') and notification_result.get('notifications_sent', 0) > 0:
                response_data['notification']['successful_mentions'] = notification_result.get('successful_mentions', [])
                response_data['message'] += f" and {notification_result.get('notifications_sent', 0)} WhatsApp notification(s) sent"
        
        return jsonify(response_data), 201
        
    except Exception as e:
        logger.error(f"Error creating note: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error creating note: {str(e)}'
        }), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

@note_bp.route('/debug/notification', methods=['GET'])
def debug_notification():
    """Debug endpoint untuk test notification system"""
    try:
        logger.info(f"Debug: NOTIFICATION_ENABLED = {NOTIFICATION_ENABLED}")
        
        if not NOTIFICATION_ENABLED:
            return jsonify({
                'status': 'error',
                'message': 'Notification system is disabled',
                'notification_enabled': NOTIFICATION_ENABLED
            }), 500
        
        # Test data
        test_note_data = {
            'id_note': 999,
            'note_title': 'Test notification for @vinka',
            'note_content': 'This is a test notification to @vinka',
            'id_input': 'debug_test',
            'table_source': 'table_design',
            'created_by': 'debug_user',
            'created_at': datetime.now().isoformat()
        }
        
        logger.info(f"Debug: Testing notification with data: {test_note_data}")
        
        # Test notification
        result = notification_handler.process_note_creation(test_note_data)
        
        logger.info(f"Debug: Notification result: {result}")
        
        return jsonify({
            'status': 'success',
            'message': 'Debug notification test completed',
            'notification_enabled': NOTIFICATION_ENABLED,
            'test_data': test_note_data,
            'notification_result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Debug notification error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Debug notification error: {str(e)}',
            'notification_enabled': NOTIFICATION_ENABLED
        }), 500

# PIN Authentication endpoint
@note_bp.route('/api/auth/verify-pin', methods=['POST'])
def verify_pin():
    try:
        data = request.get_json()
        
        # Validasi input
        if not data.get('user_name') or not data.get('pin'):
            return jsonify({
                'status': 'error',
                'message': 'user_name and pin are required'
            }), 400
        
        user_name = data['user_name']
        pin = data['pin']
        
        # Cek apakah user_name valid
        if user_name not in USER_PINS:
            return jsonify({
                'status': 'error',
                'message': 'Invalid user name'
            }), 400
        
        # Verifikasi PIN
        if USER_PINS[user_name] == pin:
            logger.info(f"PIN verification successful for user: {user_name}")
            return jsonify({
                'status': 'success',
                'message': 'PIN verified successfully',
                'user_name': user_name
            }), 200
        else:
            logger.warning(f"PIN verification failed for user: {user_name}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid PIN'
            }), 401
        
    except Exception as e:
        logger.error(f"Error verifying PIN: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error verifying PIN: {str(e)}'
        }), 500

# READ - Get ALL notes by id_input (for Existing Notes field)
@note_bp.route('/api/notes/<id_input>', methods=['GET'])
def get_all_notes_by_id_input(id_input):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'message': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get ALL notes for this id_input from all table_sources
        select_query = """
            SELECT id_note, id_input, table_source, note_title, note_content, 
                   created_by, created_at, updated_at, is_active
            FROM table_note 
            WHERE id_input = %s AND is_active = TRUE
            ORDER BY table_source, created_at DESC
        """
        
        cursor.execute(select_query, (id_input,))
        notes = cursor.fetchall()
        
        # Format datetime untuk JSON serialization
        for note in notes:
            if note['created_at']:
                note['created_at'] = note['created_at'].isoformat()
            if note['updated_at']:
                note['updated_at'] = note['updated_at'].isoformat()
        
        # Group notes by table_source for better organization
        grouped_notes = {
            'table_design': [],
            'table_produksi': [],
            'table_pesanan': []
        }
        
        for note in notes:
            if note['table_source'] in grouped_notes:
                grouped_notes[note['table_source']].append(note)
        
        return jsonify({
            'status': 'success',
            'data': notes,
            'grouped_data': grouped_notes,
            'count': len(notes)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting all notes: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error getting all notes: {str(e)}'
        }), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# READ - Get notes by id_input and table_source
@note_bp.route('/api/notes/<id_input>/<table_source>', methods=['GET'])
def get_notes(id_input, table_source):
    try:
        # Validasi table_source
        valid_sources = ['table_design', 'table_produksi', 'table_pesanan']
        if table_source not in valid_sources:
            return jsonify({
                'status': 'error',
                'message': 'Invalid table_source'
            }), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'message': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get notes
        select_query = """
            SELECT id_note, id_input, table_source, note_title, note_content, 
                   created_by, created_at, updated_at, is_active
            FROM table_note 
            WHERE id_input = %s AND table_source = %s AND is_active = TRUE
            ORDER BY created_at DESC
        """
        
        cursor.execute(select_query, (id_input, table_source))
        notes = cursor.fetchall()
        
        # Format datetime untuk JSON serialization
        for note in notes:
            if note['created_at']:
                note['created_at'] = note['created_at'].isoformat()
            if note['updated_at']:
                note['updated_at'] = note['updated_at'].isoformat()
        
        return jsonify({
            'status': 'success',
            'data': notes,
            'count': len(notes)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting notes: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error getting notes: {str(e)}'
        }), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# UPDATE - Update note
@note_bp.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    try:
        data = request.get_json()
        
        # Validasi input
        if not data.get('note_title') and not data.get('note_content'):
            return jsonify({
                'status': 'error',
                'message': 'At least note_title or note_content must be provided'
            }), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'message': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Check if note exists
        cursor.execute("SELECT id_note FROM table_note WHERE id_note = %s AND is_active = TRUE", (note_id,))
        if not cursor.fetchone():
            return jsonify({
                'status': 'error',
                'message': 'Note not found'
            }), 404
        
        # Build update query dynamically
        update_fields = []
        update_values = []
        
        if data.get('note_title'):
            update_fields.append('note_title = %s')
            update_values.append(data['note_title'])
        
        if data.get('note_content'):
            update_fields.append('note_content = %s')
            update_values.append(data['note_content'])
        
        update_fields.append('updated_at = %s')
        update_values.append(datetime.now())
        update_values.append(note_id)
        
        update_query = f"UPDATE table_note SET {', '.join(update_fields)} WHERE id_note = %s"
        
        cursor.execute(update_query, update_values)
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({
                'status': 'error',
                'message': 'No changes made'
            }), 400
        
        logger.info(f"Note {note_id} updated successfully")
        
        return jsonify({
            'status': 'success',
            'message': 'Note updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating note: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error updating note: {str(e)}'
        }), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# DELETE - Soft delete note
@note_bp.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'message': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor()
        
        # Check if note exists
        cursor.execute("SELECT id_note FROM table_note WHERE id_note = %s AND is_active = TRUE", (note_id,))
        if not cursor.fetchone():
            return jsonify({
                'status': 'error',
                'message': 'Note not found'
            }), 404
        
        # Soft delete (set is_active = FALSE)
        delete_query = "UPDATE table_note SET is_active = FALSE, updated_at = %s WHERE id_note = %s"
        cursor.execute(delete_query, (datetime.now(), note_id))
        conn.commit()
        
        logger.info(f"Note {note_id} deleted successfully")
        
        return jsonify({
            'status': 'success',
            'message': 'Note deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting note: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error deleting note: {str(e)}'
        }), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

# GET - Get single note by ID
@note_bp.route('/api/notes/<int:note_id>', methods=['GET'])
def get_note_by_id(note_id):
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                'status': 'error',
                'message': 'Database connection failed'
            }), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Get single note
        select_query = """
            SELECT id_note, id_input, table_source, note_title, note_content, 
                   created_by, created_at, updated_at, is_active
            FROM table_note 
            WHERE id_note = %s AND is_active = TRUE
        """
        
        cursor.execute(select_query, (note_id,))
        note = cursor.fetchone()
        
        if not note:
            return jsonify({
                'status': 'error',
                'message': 'Note not found'
            }), 404
        
        # Format datetime untuk JSON serialization
        if note['created_at']:
            note['created_at'] = note['created_at'].isoformat()
        if note['updated_at']:
            note['updated_at'] = note['updated_at'].isoformat()
        
        return jsonify({
            'status': 'success',
            'data': note
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting note: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error getting note: {str(e)}'
        }), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()