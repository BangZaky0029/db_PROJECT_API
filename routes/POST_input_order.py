import os
from flask import Blueprint, jsonify, request, send_from_directory, current_app
from flask_cors import CORS
from mysql.connector import Error, InterfaceError
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_db_connection
import datetime
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint untuk input order
post_input_order_bp = Blueprint("input_order", __name__)
CORS(post_input_order_bp, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Configure file upload settings
UPLOAD_FOLDER = r"C:\KODINGAN\db_manukashop\images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# Base URL for accessing the images - configure this to match your server setup
IMAGE_BASE_URL = "http://100.117.80.112:5000/images"

# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Upload folder configuration will be added to app in the route handler

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function for CORS preflight
def _handle_cors_preflight():
    response = jsonify({"status": "success"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    return response

# Add a route to serve images
# Route untuk serve image
@post_input_order_bp.route('/images/<filename>')
def serve_image(filename):
    try:
       return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return "File not found", 404

@post_input_order_bp.route("/api/input-order", methods=["OPTIONS", "POST"])
def input_order():
    if request.method == "OPTIONS":
        return _handle_cors_preflight()

    conn, cursor = None, None
    try:
        # Check if request has form data or JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle form data with file upload
            data = request.form.to_dict()
            file = None
            if 'photo' in request.files:
                file = request.files['photo']
        else:
            # Handle JSON data (backward compatibility)
            data = request.get_json()
            if not data:
                return jsonify({"status": "error", "message": "Request body harus berupa JSON atau form data"}), 400
            file = None

        # Validate required fields
        required_fields = ["id_pesanan", "id_admin", "Platform", "qty", "Deadline", "id_produk", "id_type"]
        missing_fields = [field for field in required_fields if field not in data or not str(data[field]).strip()]
        if missing_fields:
            return jsonify({"status": "error", "message": f"Field berikut wajib diisi: {', '.join(missing_fields)}"}), 400

        # Get data from request
        id_pesanan = data["id_pesanan"].strip()
        id_admin = data["id_admin"].strip()
        platform = data["Platform"].strip()
        qty = int(data["qty"])
        deadline = data["Deadline"].strip()
        id_produk = int(data["id_produk"])
        id_type = int(data["id_type"])
        nama_ket = data.get("nama_ket", "").strip()
        id_designer = data.get("id_designer") or None
        id_penjahit = data.get("id_penjahit") or None
        id_qc = data.get("id_qc") or None

        # Handle file upload
        link = data.get("link", "").strip()
        if file and file.filename != '':
            if allowed_file(file.filename):
                # Generate unique filename with timestamp to avoid conflicts
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                filename = secure_filename(f"{timestamp}_{file.filename}")
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                # Save file
                file.save(filepath)
                logger.info(f"File saved successfully: {filepath}")
                
                # Convert local path to web URL
                link = f"{IMAGE_BASE_URL}/{filename}"
                logger.info(f"Converted path to URL: {link}")
            else:
                return jsonify({
                    "status": "error", 
                    "message": f"Format file tidak didukung. Format yang diizinkan: {', '.join(ALLOWED_EXTENSIONS)}"
                }), 400

        # Log data for debugging
        logger.info(f"Processing order with id_pesanan: {id_pesanan}, id_produk: {id_produk}")

        # Get current time
        now = datetime.datetime.now()
        bulan = now.strftime("%m")
        tahun = now.strftime("%y")
        current_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        # Connect to database
        conn = get_db_connection()
        if conn is None:
            return jsonify({"status": "error", "message": "Gagal terhubung ke database"}), 500

        cursor = conn.cursor(dictionary=True, buffered=True)  # Use buffered cursor to avoid unread results

        # Verify the existence of id_produk in the referenced table
        cursor.execute("SELECT id_produk FROM table_produk WHERE id_produk = %s", (id_produk,))
        produk = cursor.fetchone()
        if not produk:
            return jsonify({
                "status": "error", 
                "message": f"ID Produk {id_produk} tidak ditemukan dalam database"
            }), 400

        # Generate unique ID with NULL handling
        cursor.execute("SELECT id_input FROM table_input_order WHERE id_input LIKE %s ORDER BY id_input DESC LIMIT 1", (f"{bulan}{tahun}-%",))
        last_id = cursor.fetchone()
        
        if last_id and last_id.get('id_input'):
            last_num = int(last_id['id_input'].split("-")[1]) + 1
        else:
            last_num = 1
            
        id_input = f"{bulan}{tahun}-{str(last_num).zfill(5)}"
        logger.info(f"Generated id_input: {id_input}")

        # Begin transaction
        conn.start_transaction()

        # INSERT into table_input_order
        try:
            cursor.execute(
                """
                INSERT INTO table_input_order 
                (id_input, id_produk, TimeTemp, id_pesanan, id_admin, Platform, qty, nama_ket, link, Deadline, id_type) 
                VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (id_input, id_produk, id_pesanan, id_admin, platform, qty, nama_ket, link, deadline, id_type)
            )
            logger.info("Successfully inserted into table_input_order")
        except Error as e:
            logger.error(f"Error inserting into table_input_order: {str(e)}")
            conn.rollback()
            return jsonify({"status": "error", "message": f"Error inserting into table_input_order: {str(e)}"}), 500

        # INSERT into table_pesanan
        try:
            cursor.execute(
                """
                INSERT INTO table_pesanan 
                (id_pesanan, id_input, platform, id_admin, qty, deadline, 
                id_desainer, timestamp_designer, id_penjahit, timestamp_penjahit, 
                id_qc, timestamp_qc, status_print, status_produksi, id_produk, id_type) 
                VALUES (%s, %s, %s, %s, %s, %s, 
                        %s, %s, %s, %s, 
                        %s, %s, '-', '-', %s, %s)
                """,
                (id_pesanan, id_input, platform, id_admin, qty, deadline, 
                id_designer, current_timestamp if id_designer else None,
                id_penjahit, current_timestamp if id_penjahit else None,
                id_qc, current_timestamp if id_qc else None,
                id_produk, id_type)
            )
            logger.info("Successfully inserted into table_pesanan")
        except Error as e:
            logger.error(f"Error inserting into table_pesanan: {str(e)}")
            conn.rollback()
            return jsonify({"status": "error", "message": f"Error inserting into table_pesanan: {str(e)}"}), 500

        # INSERT into table_prod
        try:
            cursor.execute(
                """
                INSERT INTO table_prod 
                (id_input, id_pesanan, platform, qty, deadline, status_print, status_produksi, id_produk, id_type)
                VALUES (%s, %s, %s, %s, %s, '-', '-', %s, %s)
                """,
                (id_input, id_pesanan, platform, qty, deadline, id_produk, id_type)
            )
            logger.info("Successfully inserted into table_prod")
        except Error as e:
            logger.error(f"Error inserting into table_prod: {str(e)}")
            conn.rollback()
            return jsonify({"status": "error", "message": f"Error inserting into table_prod: {str(e)}"}), 500

        # INSERT into table_design
        try:
            cursor.execute(
                """
                INSERT INTO table_design 
                (id_input, id_pesanan, id_designer, platform, qty, layout_link, deadline, status_print, timestamp, id_produk, id_type)
                VALUES (%s, %s, %s, %s, %s, %s, %s, '-', NOW(), %s, %s)
                """,
                (id_input, id_pesanan, id_designer, platform, qty, None, deadline, id_produk, id_type)
            )
            logger.info("Successfully inserted into table_design")
        except Error as e:
            logger.error(f"Error inserting into table_design: {str(e)}")
            conn.rollback()
            return jsonify({"status": "error", "message": f"Error inserting into table_design: {str(e)}"}), 500

        # Check if deadline is today, insert into table_urgent
        try:
            cursor.execute("SELECT CURDATE()")
            current_date = cursor.fetchone()['CURDATE()']

            if deadline == str(current_date):
                cursor.execute(
                    """
                    INSERT INTO table_urgent 
                    (id_input, id_pesanan, platform, qty, deadline, status_print, status_produksi, id_produk, id_type)
                    VALUES (%s, %s, %s, %s, %s, '-', '-', %s, %s)
                    """,
                    (id_input, id_pesanan, platform, qty, deadline, id_produk, id_type)
                )
                logger.info("Successfully inserted into table_urgent")
        except Error as e:
            logger.error(f"Error handling table_urgent: {str(e)}")
            conn.rollback()
            return jsonify({"status": "error", "message": f"Error handling table_urgent: {str(e)}"}), 500

        # Commit transaction
        conn.commit()
        logger.info(f"Successfully committed transaction for order {id_pesanan}")

        response = jsonify({
            "status": "success",
            "message": "Data Berhasil Terinput dengan ID : {}".format(id_input),
            "data": {
                "id_input": id_input,
                "id_pesanan": id_pesanan,
                "id_admin": id_admin,
                "Platform": platform,
                "qty": qty,
                "nama_ket": nama_ket,
                "link": link,
                "Deadline": deadline,
                "id_type": id_type,
                "id_produk": id_produk,
                "TimeTemp": current_timestamp
            }
        })
        
        # Set CORS headers to prevent refresh issues
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Cache-Control", "no-cache, no-store, must-revalidate")
        
        return response, 201

    except (ValueError, InterfaceError) as e:
        logger.error(f"Value or Interface Error: {str(e)}")
        if conn:
            conn.rollback()
        response = jsonify({"status": "error", "message": f"Kesalahan: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Cache-Control", "no-cache, no-store, must-revalidate")
        return response, 500
    except Error as e:
        logger.error(f"MySQL Error: {str(e)}")
        if conn:
            conn.rollback()
        response = jsonify({"status": "error", "message": f"Kesalahan database: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Cache-Control", "no-cache, no-store, must-revalidate")
        return response, 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        response = jsonify({"status": "error", "message": f"Kesalahan sistem: {str(e)}"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Cache-Control", "no-cache, no-store, must-revalidate")
        return response, 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Connection and cursor closed")

# Don't forget to import send_from_directory at the top of your file
from flask import send_from_directory




# Fungsi untuk menangani request OPTIONS (CORS Preflight)
def _handle_cors_preflight():
    response = jsonify({"status": "success", "message": "Preflight OK"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response, 200




# # Folder penyimpanan foto
# UPLOAD_FOLDER = r"D:\KODINGAN\BELAJAR KODING\WebKoding\MNK-DASHBOARD\db_mnk\images"

# # Buat folder jika belum ada
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# # Tambahin konfigurasi folder upload ke app
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# # Endpoint POST untuk menyimpan foto
# @post_input_order_bp.route('/api/upload-foto', methods=['POST'])
# def upload_foto():
#     if 'file' not in request.files:
#         return jsonify({"status": "error", "message": "File tidak ditemukan"}), 400

#     file = request.files['file']

#     # Cek apakah ada file yang di-upload
#     if file.filename == '':
#         return jsonify({"status": "error", "message": "Tidak ada file yang dipilih"}), 400

#     try:
#         # Amankan nama file
#         filename = secure_filename(file.filename)
#         filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

#         # Simpan file ke folder
#         file.save(filepath)
#         logger.info(f"File berhasil disimpan: {filepath}")

#         # Simpan path ke database
#         conn = get_db_connection()
#         if conn is None:
#             return jsonify({"status": "error", "message": "Koneksi ke database gagal"}), 500
#         cursor = conn.cursor()

#         sql = "INSERT INTO table_foto (foto) VALUES (%s)"
#         cursor.execute(sql, (filepath,))
#         conn.commit()

#         # Tutup koneksi
#         cursor.close()
#         conn.close()

#         return jsonify({"status": "success", "message": "Foto berhasil diunggah", "path": filepath}), 201
#     except Exception as e:
#         logger.error(f"Error uploading file: {str(e)}")
#         return jsonify({"status": "error", "message": str(e)}), 500