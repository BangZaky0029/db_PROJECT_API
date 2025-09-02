from flask import Blueprint, request, jsonify, Flask, send_from_directory
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_db_connection
import logging
import os
from werkzeug.utils import secure_filename
import datetime

# 🔹 Inisialisasi Flask
app = Flask(__name__)
CORS(app)

# 🔹 Inisialisasi Blueprint
update_design_bp = Blueprint('design', __name__)
CORS(update_design_bp)

# 🔹 Konfigurasi Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add these configurations
UPLOAD_FOLDER = r"C:\KODINGAN\db_manukashop\images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
IMAGE_BASE_URL = "http://100.124.58.32:5000/images"

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return "Server Flask berjalan!"

def execute_update(query, values, conn, cursor):
    """ Helper untuk eksekusi query update dengan logging """
    try:
        cursor.execute(query, values)
        conn.commit()
        logger.info(f"✅ Update berhasil: {query} dengan {values}")
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error update: {str(e)}")
        raise

def sync_tables(id_input, conn, cursor, columns=None):
    """ Sinkronisasi table_pesanan dan table_prod """
    cursor.execute("""
        UPDATE table_pesanan p
        JOIN table_design d ON p.id_input = d.id_input
        SET 
            p.id_desainer = d.id_designer,
            p.layout_link = d.layout_link,
            p.status_print = d.status_print
        WHERE p.id_input = %s
    """, (id_input,))
    
    # 🔹 Tambahkan update timestamp_designer jika id_designer diperbarui
    if columns and "id_designer" in columns:
        cursor.execute("""
            UPDATE table_pesanan 
            SET id_desainer = %s, 
                timestamp_designer = COALESCE(timestamp_designer, CURRENT_TIMESTAMP) 
            WHERE id_input = %s
        """, (columns["id_designer"], id_input))
        logger.info(f"✅ id_desainer dan timestamp_designer diperbarui untuk id_input: {id_input}")

    if columns and "status_print" in columns:
        cursor.execute("UPDATE table_prod SET status_print = %s WHERE id_input = %s", (columns["status_print"], id_input))
        logger.info(f"✅ status_print diperbarui di table_prod untuk id_input: {id_input}")
        cursor.execute("UPDATE table_urgent SET status_print = %s WHERE id_input = %s", (columns["status_print"], id_input))
        logger.info(f"✅ status_print diperbarui di table_urgent untuk id_input: {id_input}")


@update_design_bp.route('/api/update-design', methods=['PUT'])
def update_design():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        data = request.get_json()
        id_input = data.get('id_input')
        if not id_input:
            return jsonify({'status': 'error', 'message': 'id_input wajib diisi'}), 400

        cursor.execute("SELECT id_input FROM table_design WHERE id_input = %s", (id_input,))
        if not cursor.fetchone():
            return jsonify({'status': 'error', 'message': 'Data tidak ditemukan di table_design'}), 404

        update_fields = {k: v for k, v in data.items() if k in ["id_designer", "layout_link", "status_print"] and v is not None}
        if update_fields:
            query = "UPDATE table_design SET " + ", ".join(f"{k} = %s" for k in update_fields.keys()) + " WHERE id_input = %s"
            execute_update(query, list(update_fields.values()) + [id_input], conn, cursor)
            sync_tables(id_input, conn, cursor, update_fields)

        return jsonify({'status': 'success', 'message': 'Data berhasil diperbarui & disinkronkan'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@update_design_bp.route('/api/update-print-status-layout', methods=['PUT'])
def update_print_status():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        data = request.get_json()
        id_input, column, value = data.get('id_input'), data.get('column'), data.get('value')
        allowed_columns = ["id_designer", "status_print", "layout_link", "platform", "qty", "deadline"]

        if column not in allowed_columns:
            return jsonify({'status': 'error', 'message': 'Kolom tidak valid'}), 400
        
        execute_update(f"UPDATE table_design SET {column} = %s WHERE id_input = %s", (value, id_input), conn, cursor)
        sync_tables(id_input, conn, cursor, {column: value} if column == "status_print" else None)
        
        return jsonify({'status': 'success', 'message': f'{column} berhasil diperbarui & disinkronkan'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@update_design_bp.route('/api/update-layout', methods=['POST'])
def update_layout():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        id_input = request.form.get('id_input')
        if not id_input:
            return jsonify({'status': 'error', 'message': 'id_input wajib diisi'}), 400

        if 'layout_file' not in request.files:
            return jsonify({'status': 'error', 'message': 'File tidak ditemukan'}), 400

        file = request.files['layout_file']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'Tidak ada file yang dipilih'}), 400

        if file and allowed_file(file.filename):
            # Generate unique filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            filename = secure_filename(f"layout_{timestamp}_{file.filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save file
            file.save(filepath)
            
            # Create URL for database
            layout_url = f"{IMAGE_BASE_URL}/{filename}"

            # Update table_design
            execute_update(
                "UPDATE table_design SET layout_link = %s WHERE id_input = %s",
                (layout_url, id_input),
                conn,
                cursor
            )

            # Sync with other tables
            cursor.execute("""
                UPDATE table_pesanan
                SET layout_link = %s
                WHERE id_input = %s
            """, (layout_url, id_input))

            return jsonify({
                'status': 'success',
                'message': 'Layout berhasil diupload dan diupdate',
                'layout_url': layout_url
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': f'Format file tidak didukung. Format yang diizinkan: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

    except Exception as e:
        logger.error(f"Error updating layout: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Add route to serve images
@update_design_bp.route('/images/<filename>')
def serve_image(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return "File not found", 404
