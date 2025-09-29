from flask import Blueprint, request, jsonify, Flask
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_db_connection
import logging
import mysql.connector

# 🔹 Inisialisasi Flask
app = Flask(__name__)
CORS(app)

# 🔹 Initialize Blueprint
sync_prod_bp = Blueprint('sync_prod', __name__)
CORS(sync_prod_bp)

# 🔹 Configure Logger
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_db_columns(table_name):
    """ Retrieve column names for a given table """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        return [column[0] for column in cursor.fetchall()]
    except mysql.connector.Error as e:
        logger.error(f"❌ Error retrieving columns for {table_name}: {e}")
        return []
    finally:
        if conn:
            conn.close()

def validate_input(id_input):
    """ Validasi apakah id_input ada di database """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Cek keberadaan id_input di tabel yang diperlukan
        tables_to_check = ['table_prod', 'table_pesanan']
        for table in tables_to_check:
            cursor.execute(f"SELECT 1 FROM {table} WHERE id_input = %s", (id_input,))
            if not cursor.fetchone():
                return False, f'Data tidak ditemukan di {table}'
        
        return True, None
    except mysql.connector.Error as e:
        logger.error(f"❌ Validation Error: {e}")
        return False, 'Kesalahan validasi database'
    finally:
        if conn:
            conn.close()

def execute_update(query, values):
    """ Eksekusi query update dengan commit dan error handling """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, values)
        conn.commit()
        return True, None
    except mysql.connector.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"❌ Error executing query: {e}")
        return False, str(e)
    finally:
        if conn:
            conn.close()

@sync_prod_bp.route('/api/sync-prod-to-pesanan', methods=['PUT'])
def sync_prod_to_pesanan():
    try:
        if request.content_type != "application/json":
            return jsonify({"status": "error", "message": "Invalid Content-Type"}), 400
        
        data = request.get_json()
        id_input = data.get('id_input')
        
        if not id_input:
            return jsonify({'status': 'error', 'message': 'id_input required'}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Batch all updates in a single transaction
        conn.start_transaction()
        
        try:
            # Check existence once
            cursor.execute("""
                SELECT EXISTS(SELECT 1 FROM table_prod WHERE id_input = %s) as prod,
                       EXISTS(SELECT 1 FROM table_pesanan WHERE id_input = %s) as pesanan
            """, (id_input, id_input))
            result = cursor.fetchone()
            
            if not (result['prod'] and result['pesanan']):
                conn.rollback()
                return jsonify({'status': 'error', 'message': 'Data not found'}), 404

            # Prepare update fields
            update_fields = []
            update_values = []

            # Mapping field secara dinamis berdasarkan tabel
            table_fields = {
                'table_prod': get_db_columns('table_prod'),
                'table_pesanan': get_db_columns('table_pesanan'),
                'table_design': get_db_columns('table_design'),
                'table_urgent': get_db_columns('table_urgent')
            }

            for field in ['id_penjahit', 'id_qc', 'status_produksi', 'OUT_DLN']:
                if data.get(field) is not None:
                    update_fields.append(f"{field} = %s")
                    update_values.append(data[field])

            if not update_fields:
                conn.rollback()
                return jsonify({'status': 'error', 'message': 'No data to update'}), 400

            # Add id_input to values
            update_values.append(id_input)

            # Batch execute updates dengan validasi field
            for table, fields in table_fields.items():
                valid_update_fields = [f for f in update_fields if f.split(' = ')[0] in fields]
                if valid_update_fields:
                    update_sql = f"UPDATE {table} SET {', '.join(valid_update_fields)} WHERE id_input = %s"
                    cursor.execute(update_sql, update_values)

            conn.commit()
            return jsonify({'status': 'success', 'message': 'Update successful'}), 200

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        logger.error(f"Update error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
