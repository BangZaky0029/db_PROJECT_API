from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from project_api.db import get_db_connection
from mysql.connector import Error
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('order_sync')

app = Flask(__name__)
orders_bp = Blueprint('orders', __name__)
CORS(orders_bp)

# Reference data for names
reference_data = {
    "table_admin": [
        {"ID": 1001, "nama": "Lilis"},
        {"ID": 1002, "nama": "Ina"},
        {"ID": 1003, "nama": "Indy"},
        {"ID": 1004, "nama": "Untung"},
    ],
    "table_desainer": [
        {"ID": 1101, "nama": "IMAM"},
        {"ID": 1102, "nama": "JHODI"},
        {"ID": 1103, "nama": "ZAKY"}
    ],
    "table_kurir": [
        {"ID": 1501, "nama": "teddy"},
        {"ID": 1502, "nama": "Mas Nur"},
        {"ID": 1503, "nama": "Jhodi"}
    ],
    "table_penjahit": [
        {"ID": 1301, "nama": "Mas Ari"},
        {"ID": 1302, "nama": "Mas Saep"},
        {"ID": 1303, "nama": "Mas Egeng"},
        {"ID": 1304, "nama": "Maman"},
        {"ID": 1305, "nama": "Mas Uu"}
    ],
    "table_qc": [
        {"ID": 1401, "nama": "tita"},
        {"ID": 1402, "nama": "ina"},
        {"ID": 1403, "nama": "lilis"}
    ],
    "table_type_produk": [
        {"id_type": 45001, "kategori": "RS"},
        {"id_type": 45002, "kategori": "Non-RS"}
    ],
     "table_produk": [
        {"id_produk": 47001, "nama_produk": "MNK-Large", "id_bahan": 46001},
        {"id_produk": 47002, "nama_produk": "MNK-Medium", "id_bahan": 46001},
        {"id_produk": 47003, "nama_produk": "MNK-Small", "id_bahan": 46001},
        {"id_produk": 47004, "nama_produk": "MNK-Mini", "id_bahan": 46001},
        {"id_produk": 47005, "nama_produk": "MNK-Middle", "id_bahan": 46001},
        {"id_produk": 47006, "nama_produk": "Travel Bag", "id_bahan": 46001},
        {"id_produk": 47007, "nama_produk": "ToteBag Large", "id_bahan": 46001},
        {"id_produk": 47008, "nama_produk": "Kawai", "id_bahan": 46001},
        {"id_produk": 47009, "nama_produk": "Mini Sling", "id_bahan": 46001},
        {"id_produk": 47010, "nama_produk": "Medium Sling", "id_bahan": 46001},
        {"id_produk": 47011, "nama_produk": "Gym Bag", "id_bahan": 46001},
        {"id_produk": 47012, "nama_produk": "Darla", "id_bahan": 46001},
        {"id_produk": 47013, "nama_produk": "Bolster", "id_bahan": 46001},
        {"id_produk": 47014, "nama_produk": "Indie Bag", "id_bahan": 46001},
        {"id_produk": 47015, "nama_produk": "Mobile Bag", "id_bahan": 46001},
        {"id_produk": 47072, "nama_produk": "Scarf", "id_bahan": 46001},
        {"id_produk": 47016, "nama_produk": "Dompet type-1", "id_bahan": 46002},
        {"id_produk": 47017, "nama_produk": "Card Holder", "id_bahan": 46002},
        {"id_produk": 47018, "nama_produk": "Lanyard", "id_bahan": 46002},
        {"id_produk": 47019, "nama_produk": "Anna Karenina", "id_bahan": 46002},
        {"id_produk": 47020, "nama_produk": "Lily Bag", "id_bahan": 46002},
        {"id_produk": 47021, "nama_produk": "Puffy Laptop Zipper", "id_bahan": 46003},
        {"id_produk": 47022, "nama_produk": "Puffy Laptop Handle", "id_bahan": 46003},
        {"id_produk": 47023, "nama_produk": "Puffy Laptop HandZip", "id_bahan": 46003},
        {"id_produk": 47024, "nama_produk": "Puffy Kanaya", "id_bahan": 46003},
        {"id_produk": 47025, "nama_produk": "Puffy Karissa", "id_bahan": 46003},
        {"id_produk": 47026, "nama_produk": "Puffy Kalandra", "id_bahan": 46003},
        {"id_produk": 47027, "nama_produk": "Puffy Kalia", "id_bahan": 46003},
        {"id_produk": 47028, "nama_produk": "Puffy Table", "id_bahan": 46003},
        {"id_produk": 47029, "nama_produk": "Puffy Loly Bag", "id_bahan": 46003},
        {"id_produk": 47030, "nama_produk": "Puffy Adel Rantai", "id_bahan": 46003},
        {"id_produk": 47031, "nama_produk": "Marsoto", "id_bahan": 46004},
        {"id_produk": 47032, "nama_produk": "Clutch", "id_bahan": 46005},
        {"id_produk": 47033, "nama_produk": "Pouch Sejadah", "id_bahan": 46005},
        {"id_produk": 47034, "nama_produk": "Sejadah Rumbai", "id_bahan": 46005},
        {"id_produk": 47035, "nama_produk": "Sejadah Rumbai Anti-Slip", "id_bahan": 46005},
        {"id_produk": 47036, "nama_produk": "Sejadah Biasa", "id_bahan": 46005},
        {"id_produk": 47037, "nama_produk": "Sejadah Biasa Anti-Slip", "id_bahan": 46005},
        {"id_produk": 47038, "nama_produk": "Sejadah Mini", "id_bahan": 46005},
        {"id_produk": 47039, "nama_produk": "Sejadah Mini Rumbai", "id_bahan": 46005},
        {"id_produk": 47040, "nama_produk": "Pouch Make-up Puffy", "id_bahan": 46003},
        {"id_produk": 47041, "nama_produk": "Pouch Make-up", "id_bahan": 46003},
        {"id_produk": 47042, "nama_produk": "Mukena Print", "id_bahan": 46006},
        {"id_produk": 47043, "nama_produk": "Mukena Polos", "id_bahan": 46008},
        {"id_produk": 47044, "nama_produk": "MNK-Kulit", "id_bahan": 46002},
        {"id_produk": 47045, "nama_produk": "MNK-Paku", "id_bahan": 46001},
        {"id_produk": 47046, "nama_produk": "Alana Ransel", "id_bahan": 46001},
        {"id_produk": 47047, "nama_produk": "MNK-Velvet-L", "id_bahan": 46009},
        {"id_produk": 47048, "nama_produk": "MNK-Velvet-M", "id_bahan": 46009},
        {"id_produk": 47049, "nama_produk": "MNK-Velvet-S", "id_bahan": 46009},
        {"id_produk": 47050, "nama_produk": "MNK-Velvet-Middle", "id_bahan": 46009},
        {"id_produk": 47051, "nama_produk": "MNK-Velvet-Mini", "id_bahan": 46009},
        {"id_produk": 47052, "nama_produk": "ToteBag Large-Velvet", "id_bahan": 46009},
        {"id_produk": 47053, "nama_produk": "SJD-Velvet", "id_bahan": 46009},
        {"id_produk": 47054, "nama_produk": "SJD-Velvet-Rumbai", "id_bahan": 46009},
        {"id_produk": 47055, "nama_produk": "Clutch-Velvet", "id_bahan": 46009},
        {"id_produk": 47056, "nama_produk": "WaistBag", "id_bahan": 46001},
        {"id_produk": 47057, "nama_produk": "Brandon", "id_bahan": 46001},
        {"id_produk": 47058, "nama_produk": "Raine SlingBag", "id_bahan": 46001},
        {"id_produk": 47059, "nama_produk": "Laurent CrossBody Bag", "id_bahan": 46001},
        {"id_produk": 47060, "nama_produk": "SR.Cover Custom", "id_bahan": 46001},
        {"id_produk": 47061, "nama_produk": "SR.Cover XL (30 inch)", "id_bahan": 46001},
        {"id_produk": 47062, "nama_produk": "SR.Cover L (28 inch)", "id_bahan": 46001},
        {"id_produk": 47063, "nama_produk": "SR.Cover M (24 inch)", "id_bahan": 46001},
        {"id_produk": 47064, "nama_produk": "SR.Cover S (20 inch)", "id_bahan": 46001},
        {"id_produk": 47065, "nama_produk": "Cover Al Qur'an", "id_bahan": 46001},
        {"id_produk": 47066, "nama_produk": "MNK Medium 3D Edition", "id_bahan": 46001},
        {"id_produk": 47067, "nama_produk": "SR.Cover Custom-scuba", "id_bahan": 46007},
        {"id_produk": 47068, "nama_produk": "SR.Cover XL (30 inch)-scuba", "id_bahan": 46007},
        {"id_produk": 47069, "nama_produk": "SR.Cover L (28 inch)-scuba", "id_bahan": 46007},
        {"id_produk": 47070, "nama_produk": "SR.Cover M (24 inch)-scuba", "id_bahan": 46007},
        {"id_produk": 47071, "nama_produk": "SR.Cover S (20 inch)-scuba", "id_bahan": 46007},
        {"id_produk": 47073, "nama_produk": "Tas Koper Bu Ola", "id_bahan": 46010},
        {"id_produk": 47074, "nama_produk": "Renata Bag", "id_bahan": 46005},
        {"id_produk": 47075, "nama_produk": "Estelle Bag", "id_bahan": 46001},
        {"id_produk": 47076, "nama_produk": "ToteBag Large Pouch", "id_bahan": 46001},
        {"id_produk": 47077, "nama_produk": "ARA BAG", "id_bahan": 46001}


    ],
    "table_bahan": [
        {"id_bahan": 46001, "bahan": "Kanvas"},
        {"id_bahan": 46002, "bahan": "Kulit"},
        {"id_bahan": 46003, "bahan": "Nilon"},
        {"id_bahan": 46004, "bahan": "Marsoto"},
        {"id_bahan": 46005, "bahan": "Baby Kanvas"},
        {"id_bahan": 46006, "bahan": "Parasut"},
        {"id_bahan": 46007, "bahan": "Scuba"},
        {"id_bahan": 46008, "bahan": "Lain-Nya"},
        {"id_bahan": 46009, "bahan": "Velvet"},
        {"id_bahan": 46010, "bahan": "Bahan Custom"}
    ]
}

# GET: Ambil Data reference 
@orders_bp.route("/api/references", methods=["GET"])
def get_references():
    return jsonify(reference_data)


@orders_bp.route('/api/get-layout', methods=['GET'])
def get_layout():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Ambil parameter id_input dari request (default None)
        id_input = request.args.get('id_input', None)

        if id_input:
            query = "SELECT layout_link FROM table_design WHERE id_input = %s"
            cursor.execute(query, (id_input,))
        else:
            query = "SELECT id_input, layout_link FROM table_design"
            cursor.execute(query)

        result = cursor.fetchall()
        cursor.close()
        conn.close()

        # Cek apakah data ditemukan
        if not result:
            return jsonify({"message": "Data tidak ditemukan"}), 404

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# GET : Mengurutkan data berdasarkan deadline terdekat 
@orders_bp.route('/api/get_sorted_orders', methods=['GET'])
def get_sorted_orders():
    """ Mengambil dan mengurutkan pesanan berdasarkan deadline terdekat hingga terjauh """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query untuk mendapatkan data dan mengurutkan berdasarkan deadline ASC (terdekat dulu)
        cursor.execute("SELECT * FROM table_pesanan ORDER BY deadline ASC")
        result = cursor.fetchall()

        # Konversi deadline ke format YYYY-MM-DD
        for order in result:
            if order["deadline"]:
                order["deadline"] = order["deadline"].strftime("%Y-%m-%d")  # Format deadline


        cursor.close()
        conn.close()

        if result:
            return jsonify({"orders": result}), 200
        else:
            return jsonify({"error": "Tidak ada data pesanan"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# GET : id_admin from table_input_order
@orders_bp.route('/api/get_id_admin/<string:id_input>', methods=['GET'])
def get_id_admin(id_input):
    """ Mendapatkan id_admin berdasarkan id_input dari table_input_order """
    try:
        id_input = id_input.strip()  # Hapus spasi atau karakter tersembunyi
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id_admin FROM table_input_order WHERE id_input = %s", (id_input,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return jsonify({"status": "success", "id_admin": result["id_admin"]}), 200
        else:
            return jsonify({"status": "error", "message": "ID Input tidak ditemukan"}), 404

    except Exception as e:
        logger.error(f"❌ Error mendapatkan id_admin: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
# GET : nama_ket from table_input_order
@orders_bp.route('/api/get_nama_ket/<string:id_input>', methods=['GET'])
def get_nama_ket(id_input):
    """ Mendapatkan isi field nama_ket berdasarkan id_input dari table_input_order """
    try:
        id_input = id_input.strip()  # Hapus spasi atau karakter tersembunyi
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query untuk mengambil nama_ket berdasarkan id_input
        query = "SELECT nama_ket FROM table_input_order WHERE id_input = %s"
        cursor.execute(query, (id_input,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"status": "error", "message": f"Data dengan id_input '{id_input}' tidak ditemukan"}), 404

        return jsonify({"status": "success", "id_input": id_input, "nama_ket": result["nama_ket"]}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Kesalahan sistem: {str(e)}"}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Endpoint untuk mengambil semua data dari table_urgent
@orders_bp.route('/api/get_table_urgent', methods=['GET'])
def get_all_table_urgent():
    conn = None  # Inisialisasi awal
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Ambil semua data dari table_urgent
        cursor.execute("SELECT * FROM table_urgent ORDER BY deadline ASC")
        data = cursor.fetchall()

        cursor.close()
        conn.close()

        # Perbaiki format response agar sesuai dengan fetchOrders()
        return jsonify({
            "status": "success",
            "data": data
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# GET: Ambil semua data Dari table_produksi
@orders_bp.route('/api/get_table_prod', methods=['GET'])
def get_all_table_prod():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM table_prod"
        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "data": results}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
# GET: Ambil semua data Dari table_produksi
@orders_bp.route('/api/get_table_design', methods=['GET'])
def get_all_table_design():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM table_design"
        cursor.execute(query)
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "data": results}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# GET: Ambil semua data pesanan
@orders_bp.route('/api/get-orders', methods=['GET'])
def get_orders():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM table_pesanan")
        orders = cursor.fetchall()
        return jsonify({'status': 'success', 'data': orders}), 200
    except Error as e:
        logger.error(f"Error getting orders: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if conn.is_connected(): 
            cursor.close()
            conn.close()

# GET: Ambil semua data Inputable
# GET: Ambil semua data Inputable tanpa field 'link'
@orders_bp.route('/api/get-input-table', methods=['GET'])
def get_inputOrder():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Mengambil semua data kecuali field 'link'
        cursor.execute("""
            SELECT id_input, TimeTemp, id_pesanan, id_admin, Platform, qty, link, nama_ket, Deadline 
            FROM table_input_order
        """)
        orders = cursor.fetchall()
        
        return jsonify({'status': 'success', 'data': orders}), 200
    except Error as e:
        logger.error(f"Error getting input table: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if conn.is_connected(): 
            cursor.close()
            conn.close()


# Function to sync a single record from table_input_order to table_pesanan
def sync_to_pesanan(cursor, id_input):
    try:
        # Fetch the record from table_input_order
        cursor.execute("SELECT * FROM table_input_order WHERE id_input = %s", (id_input,))
        order = cursor.fetchone()
        
        if not order:
            return {'success': False, 'message': f'Order with id_input {id_input} not found'}
        
        # Check if record already exists in table_pesanan
        cursor.execute("SELECT id_input FROM table_pesanan WHERE id_input = %s", (id_input,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record
            cursor.execute("""
                UPDATE table_pesanan SET 
                id_pesanan = %s,
                qty = %s,
                platform = %s,
                deadline = %s,
                layout_link = %s,
                admin = %s,
                timestamp = NOW()
                WHERE id_input = %s
            """, (order[2], order[5], order[4], order[8], order[7], order[3], id_input))
        else:
            # Insert new record
            cursor.execute("""
                INSERT INTO table_pesanan 
                (id_pesanan, id_input, qty, platform, deadline, layout_link, admin, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            """, (order[2], id_input, order[5], order[4], order[8], order[7], order[3]))
        
        return {'success': True}
    
    except Exception as e:
        logger.error(f"Error syncing to pesanan: {str(e)}")
        return {'success': False, 'message': str(e)}



# Function to sync all records - can be called manually or periodically
def sync_all_to_pesanan():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all records from table_input_order
        cursor.execute("SELECT id_input FROM table_input_order")
        orders = cursor.fetchall()
        
        success_count = 0
        error_count = 0
        
        for order in orders:
            result = sync_to_pesanan(cursor, order['id_input'])
            if result['success']:
                success_count += 1
            else:
                error_count += 1
        
        conn.commit()
        logger.info(f"Sync completed: {success_count} successful, {error_count} failed")
        return {
            'success': True, 
            'success_count': success_count, 
            'error_count': error_count
        }
    
    except Exception as e:
        logger.error(f"Error in sync_all_to_pesanan: {str(e)}")
        if conn:
            conn.rollback()
        return {'success': False, 'message': str(e)}
    
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# PUT: Update input order with automatic sync to pesanan
@orders_bp.route('/api/update-input-order/<string:id_input>', methods=['PUT'])
def update_input_order(id_input):
    conn = None
    cursor = None
    try:
        data = request.get_json()
        id_input = id_input.strip()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if record exists
        cursor.execute("SELECT id_input FROM table_input_order WHERE id_input = %s", (id_input,))
        existing = cursor.fetchone()
        
        if not existing:
            return jsonify({'status': 'error', 'message': 'Record not found'}), 404
        
        # Update table_input_order
        update_fields = []
        update_values = []
        
        for key, value in data.items():
            # Skip id_input as it's the primary key
            if key != 'id_input':
                update_fields.append(f"{key} = %s")
                update_values.append(value)
        
        if not update_fields:
            return jsonify({'status': 'error', 'message': 'No fields to update'}), 400
        
        # Add id_input to the end of values for WHERE clause
        update_values.append(id_input)
        
        query = f"UPDATE table_input_order SET {', '.join(update_fields)} WHERE id_input = %s"
        cursor.execute(query, update_values)
        
        # Sync to table_pesanan
        sync_result = sync_to_pesanan(cursor, id_input)
        if not sync_result['success']:
            conn.rollback()
            return jsonify({'status': 'error', 'message': sync_result['message']}), 500
        
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Data berhasil diperbarui dan disinkronkan'}), 200
    
    except Exception as e:
        logger.error(f"Error updating input order: {str(e)}")
        if conn:
            conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# GET: Ambil daftar nama dari masing-masing tabel
@orders_bp.route('/api/get-names', methods=['GET'])
def get_names():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        tables = ['table_desainer', 'table_penjahit', 'table_qc', 'table_kurir', 'table_admin']
        result = {}

        for table in tables:
            query = f"SELECT ID, Nama FROM `{table}`"
            cursor.execute(query)
            data = cursor.fetchall()

            if not data:
                result[table] = []
            else:
                result[table] = data
        
        return jsonify({'status': 'success', 'data': result}), 200

    except Error as e:
        logger.error(f"Error getting names: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# GET: Ambil link foto berdasarkan id_input
@orders_bp.route('/api/get_link_foto/<string:id_input>', methods=['GET'])
def get_order_photo(id_input):
    try:
        id_input = id_input.strip()  # Hapus spasi, newline (\n), atau karakter tersembunyi lainnya

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT link FROM table_input_order WHERE id_input = %s"
        cursor.execute(query, (id_input,))
        data = cursor.fetchone()

        if data:
            return jsonify({
                "status": "success",
                "id_input": id_input,
                "data": data,
                "retrieved_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Data tidak ditemukan",
                "id_input": id_input,
                "retrieved_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }), 404
    except Exception as e:
        logger.error(f"Error getting photo link: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
    
# Endpoint to manually transfer orders (keep for compatibility)
@orders_bp.route('/api/transfer-orders', methods=['POST'])
def transfer_orders():
    try:
        result = sync_all_to_pesanan()
        if result['success']:
            return jsonify({
                'status': 'success', 
                'message': f'Data berhasil dipindahkan: {result["success_count"]} record berhasil'
            }), 200
        else:
            return jsonify({'status': 'error', 'message': result['message']}), 500
    except Exception as e:
        logger.error(f"Error in transfer_orders: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# POST: Create a new input order with automatic transfer to table_pesanan
@orders_bp.route('/api/create-input-order', methods=['POST'])
def create_input_order():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        required_fields = ['id_input', 'id_pesanan', 'Platform', 'qty', 'Deadline']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'status': 'error', 'message': f'Field {field} is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert into table_input_order
        fields = []
        values = []
        placeholders = []
        
        for key, value in data.items():
            fields.append(key)
            values.append(value)
            placeholders.append('%s')
        
        # Add TimeTemp field if not provided
        if 'TimeTemp' not in fields:
            fields.append('TimeTemp')
            values.append(datetime.now().strftime('%Y-%m-%d'))
            placeholders.append('%s')
        
        query = f"INSERT INTO table_input_order ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        cursor.execute(query, values)
        
        # Synchronize to table_pesanan
        sync_result = sync_to_pesanan(cursor, data['id_input'])
        if not sync_result['success']:
            conn.rollback()
            return jsonify({'status': 'error', 'message': sync_result['message']}), 500
        
        conn.commit()
        return jsonify({'status': 'success', 'message': 'Data berhasil disimpan dan disinkronkan'}), 201
    
    except Exception as e:
        logger.error(f"Error creating input order: {str(e)}")
        if conn:
            conn.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# Endpoint to manually trigger sync all
@orders_bp.route('/api/sync-all-orders', methods=['POST'])
def trigger_sync_all():
    try:
        result = sync_all_to_pesanan()
        if result['success']:
            return jsonify({
                'status': 'success', 
                'message': 'Sync completed', 
                'success_count': result['success_count'],
                'error_count': result['error_count']
            }), 200
        else:
            return jsonify({'status': 'error', 'message': result['message']}), 500
    except Exception as e:
        logger.error(f"Error triggering sync: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

# Database trigger function (will need to be implemented in MySQL as well)
def trigger_function():
    """
    This function illustrates the logic needed for a MySQL trigger.
    You'll need to implement this as an actual MySQL trigger in your database.
    """
    sql_trigger = """
    CREATE TRIGGER after_input_order_insert
    AFTER INSERT ON table_input_order
    FOR EACH ROW
    BEGIN
        INSERT INTO table_pesanan (id_pesanan, id_input, qty, platform, deadline, layout_link, admin, timestamp)
        VALUES (NEW.id_pesanan, NEW.id_input, NEW.qty, NEW.Platform, NEW.Deadline, NEW.link, NEW.ID, NOW())
        ON DUPLICATE KEY UPDATE
            id_pesanan = NEW.id_pesanan,
            qty = NEW.qty,
            platform = NEW.Platform,
            deadline = NEW.Deadline,
            layout_link = NEW.link,
            admin = NEW.ID,
            timestamp = NOW();
    END;
    
    CREATE TRIGGER after_input_order_update
    AFTER UPDATE ON table_input_order
    FOR EACH ROW
    BEGIN
        UPDATE table_pesanan
        SET
            id_pesanan = NEW.id_pesanan,
            qty = NEW.qty,
            platform = NEW.Platform,
            deadline = NEW.Deadline,
            layout_link = NEW.link,
            admin = NEW.ID,
            timestamp = NOW()
        WHERE id_input = NEW.id_input;
    END;
    
    CREATE TRIGGER after_input_order_delete
    AFTER DELETE ON table_input_order
    FOR EACH ROW
    BEGIN
        DELETE FROM table_pesanan
        WHERE id_input = OLD.id_input;
    END;
    """
    return sql_trigger