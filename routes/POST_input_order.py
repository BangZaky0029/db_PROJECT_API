from flask import Flask, Blueprint, jsonify, request
from flask_cors import CORS
from mysql.connector import Error, InterfaceError
from project_api.db import get_db_connection
import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:5501", "http://localhost:5501"]}})

# Blueprint untuk input order
post_input_order_bp = Blueprint("input_order", __name__)
CORS(post_input_order_bp)

@post_input_order_bp.route("/api/input-order", methods=["OPTIONS", "POST"])
def input_order():
    if request.method == "OPTIONS":
        return _handle_cors_preflight()

    conn, cursor = None, None
    try:
        # Validasi request JSON
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Request body harus berupa JSON"}), 400

        # Pastikan semua field wajib ada
        required_fields = ["id_pesanan", "id_admin", "Platform", "qty", "Deadline", "id_produk", "id_type"]
        missing_fields = [field for field in required_fields if field not in data or not str(data[field]).strip()]
        if missing_fields:
            return jsonify({"status": "error", "message": f"Field berikut wajib diisi: {', '.join(missing_fields)}"}), 400

        # Ambil data
        id_pesanan = data["id_pesanan"].strip()
        id_admin = data["id_admin"].strip()
        platform = data["Platform"].strip()
        qty = int(data["qty"])
        deadline = data["Deadline"].strip()
        id_produk = int(data["id_produk"])
        id_type = int(data["id_type"])
        nama_ket = data.get("nama_ket", "").strip()
        link = data.get("link", "").strip()
        id_designer = data.get("id_designer") or None
        id_penjahit = data.get("id_penjahit") or None
        id_qc = data.get("id_qc") or None

        # Log data for debugging
        logger.info(f"Processing order with id_pesanan: {id_pesanan}, id_produk: {id_produk}")

        # Waktu sekarang
        now = datetime.datetime.now()
        bulan = now.strftime("%m")
        tahun = now.strftime("%y")
        current_timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

        # Koneksi ke database
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

        # Generate unique ID dengan handling jika NULL
        cursor.execute("SELECT id_input FROM table_input_order WHERE id_input LIKE %s ORDER BY id_input DESC LIMIT 1", (f"{bulan}{tahun}-%",))
        last_id = cursor.fetchone()
        
        if last_id and last_id.get('id_input'):
            last_num = int(last_id['id_input'].split("-")[1]) + 1
        else:
            last_num = 1
            
        id_input = f"{bulan}{tahun}-{str(last_num).zfill(5)}"
        logger.info(f"Generated id_input: {id_input}")

        # Mulai transaksi
        conn.start_transaction()

        # INSERT ke table_input_order with detailed error handling
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

        # INSERT ke table_pesanan
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


        # INSERT ke table_prod
        try:
            cursor.execute(
                """
                INSERT INTO table_prod 
                (id_input, platform, qty, deadline, status_print, status_produksi, timestamp, id_produk, id_type)
                VALUES (%s, %s, %s, %s, '-', 'Pilih Status', NOW(), %s, %s)
                """,
                (id_input, platform, qty, deadline, id_produk, id_type)
            )
            logger.info("Successfully inserted into table_prod")
        except Error as e:
            logger.error(f"Error inserting into table_prod: {str(e)}")
            conn.rollback()
            return jsonify({"status": "error", "message": f"Error inserting into table_prod: {str(e)}"}), 500


        # INSERT ke table_design
        try:
            cursor.execute(
                """
                INSERT INTO table_design 
                (id_input, id_designer, platform, qty, layout_link, deadline, status_print, timestamp, id_produk, id_type)
                VALUES (%s, %s, %s, %s, %s, %s, '-', NOW(), %s, %s)
                """,
                (id_input, id_designer, platform, qty, None, deadline, id_produk, id_type)
            )
            logger.info("Successfully inserted into table_design")
        except Error as e:
            logger.error(f"Error inserting into table_design: {str(e)}")
            conn.rollback()
            return jsonify({"status": "error", "message": f"Error inserting into table_design: {str(e)}"}), 500


        # Jika deadline = NOW(), masukkan juga ke table_urgent
        try:
            cursor.execute("SELECT CURDATE()")
            current_date = cursor.fetchone()['CURDATE()']

            if deadline == str(current_date):
                cursor.execute(
                    """
                    INSERT INTO table_urgent 
                    (id_input, id_pesanan, platform, qty, deadline, status_print, status_produksi, id_produk, id_type)
                    VALUES (%s, %s, %s, %s, %s, '-', 'Pilih Status', %s, %s)
                    """,
                    (id_input, id_pesanan, platform, qty, deadline, id_produk, id_type)
                )
                logger.info("Successfully inserted into table_urgent")
        except Error as e:
            logger.error(f"Error handling table_urgent: {str(e)}")
            conn.rollback()
            return jsonify({"status": "error", "message": f"Error handling table_urgent: {str(e)}"}), 500

        # Commit transaksi
        conn.commit()
        logger.info(f"Successfully committed transaction for order {id_pesanan}")

        return jsonify({
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
        }), 201

    except (ValueError, InterfaceError) as e:
        logger.error(f"Value or Interface Error: {str(e)}")
        if conn:
            conn.rollback()
        return jsonify({"status": "error", "message": f"Kesalahan: {str(e)}"}), 500
    except Error as e:
        logger.error(f"MySQL Error: {str(e)}")
        if conn:
            conn.rollback()
        return jsonify({"status": "error", "message": f"Kesalahan database: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"status": "error", "message": f"Kesalahan sistem: {str(e)}"}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.info("Connection and cursor closed")

# Register blueprint
app.register_blueprint(post_input_order_bp)

# Fungsi untuk menangani request OPTIONS (CORS Preflight)
def _handle_cors_preflight():
    response = jsonify({"status": "success", "message": "Preflight OK"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response, 200

if __name__ == "__main__":
    app.run(debug=True)