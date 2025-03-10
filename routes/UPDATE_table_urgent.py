from flask import Blueprint, Flask, request, jsonify
from project_api.db import get_db_connection
import logging
from flask_cors import CORS

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

update_urgent_bp = Blueprint('update_urgent_bp', __name__)
CORS(update_urgent_bp)  # Apply CORS at the Blueprint level

# Endpoint untuk update status_print dan status_produksi ke table_urgent
@update_urgent_bp.route('/api/update_status_urgent', methods=['PUT', 'OPTIONS'])
def update_status_urgent():
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({"status": "success", "message": "Preflight OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "PUT, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 200
        
    conn = None
    cursor = None
    try:
        data = request.json
        if not data or 'id_input' not in data:
            logger.error("Missing id_input in request body")
            return jsonify({"error": "id_input diperlukan"}), 400
            
        id_input = data.get("id_input")
        logger.info(f"Received request to update_status_urgent with id_input: {id_input}")
        
        conn = get_db_connection()
        if not conn:
            logger.error("Database connection failed")
            return jsonify({"error": "Gagal terhubung ke database"}), 500
            
        cursor = conn.cursor()

        # First, check if the id_input exists in table_urgent
        cursor.execute("SELECT id_input FROM table_urgent WHERE id_input = %s", (id_input,))
        urgent_data = cursor.fetchone()
        if not urgent_data:
            logger.warning(f"id_input {id_input} not found in table_urgent")
            # Insert new record if it doesn't exist
            cursor.execute("""
                INSERT INTO table_urgent (id_input, status_print, status_produksi)
                VALUES (%s, '-', 'Pilih Status')
            """, (id_input,))
            logger.info(f"Created new record in table_urgent for id_input {id_input}")
        
        # Get current status values
        cursor.execute("SELECT status_print FROM table_design WHERE id_input = %s", (id_input,))
        design_data = cursor.fetchone()
        if not design_data:
            logger.warning(f"id_input {id_input} not found in table_design")
            return jsonify({"error": f"id_input {id_input} tidak ditemukan di table_design"}), 404

        cursor.execute("SELECT status_produksi FROM table_prod WHERE id_input = %s", (id_input,))
        prod_data = cursor.fetchone()
        if not prod_data:
            logger.warning(f"id_input {id_input} not found in table_prod")
            return jsonify({"error": f"id_input {id_input} tidak ditemukan di table_prod"}), 404

        # Get the actual values from the tuples
        status_print = design_data[0] if design_data else '-'
        status_produksi = prod_data[0] if prod_data else 'Pilih Status'
        
        # Direct update with explicit values
        cursor.execute("""
            UPDATE table_urgent 
            SET status_print = %s, status_produksi = %s
            WHERE id_input = %s
        """, (status_print, status_produksi, id_input))
        
        rows_affected = cursor.rowcount
        logger.info(f"Updated table_urgent for id_input {id_input}, rows affected: {rows_affected}")

        conn.commit()
        
        return jsonify({
            "success": True, 
            "message": "Status updated successfully",
            "data": {
                "id_input": id_input,
                "status_print": status_print,
                "status_produksi": status_produksi,
                "rows_affected": rows_affected
            }
        }), 200

    except Exception as e:
        logger.error(f"Error updating status: {str(e)}")
        if conn:
            conn.rollback()
        return jsonify({"error": f"Gagal memperbarui status: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()