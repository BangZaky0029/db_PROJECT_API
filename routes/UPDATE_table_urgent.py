from flask import Blueprint, Flask, make_response, request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_db_connection
import logging
from flask_cors import CORS

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

update_urgent_bp = Blueprint('update_urgent_bp', __name__)
CORS(update_urgent_bp)  # Apply CORS at the Blueprint level

@update_urgent_bp.route('/api/move_to_urgent', methods=['POST', 'OPTIONS'])
def move_to_urgent():
    if request.method == 'OPTIONS':
        response = make_response(jsonify({"message": "Preflight request successful"}), 200)
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        return response

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Query untuk memindahkan data dari table_input_order ke table_urgent
        query = """
            INSERT INTO table_urgent (id_input, id_pesanan, platform, qty, deadline, id_produk, id_type)
            SELECT id_input, id_pesanan, Platform, qty, Deadline, id_produk, id_type
            FROM table_input_order
            WHERE Deadline = CURDATE()
            ON DUPLICATE KEY UPDATE
                platform = VALUES(platform),
                qty = VALUES(qty),
                deadline = VALUES(deadline),
                id_produk = VALUES(id_produk),
                id_type = VALUES(id_type)
        """
        cursor.execute(query)
        conn.commit()

        affected_rows = cursor.rowcount
        logger.info(f"Data moved to table_urgent, affected rows: {affected_rows}")

        return jsonify({"message": "Data berhasil dipindahkan ke table_urgent", "affectedRows": affected_rows}), 200

    except Exception as e:
        conn.rollback()
        logger.error(f"Error while moving data: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
