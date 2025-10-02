from flask import Blueprint, request, jsonify, send_file
import os
import json
import re
from PIL import Image, ImageDraw, ImageFont
import sys

# Blueprint setup
design_header_bp = Blueprint('design_header', __name__)

# Paths configuration
JSON_DIR = r"C:\KODINGAN\db_manukashop\images\jsonCode"
LEFT_MARKER_PATH = r"C:\KODINGAN\db_manukashop\images\kotak\left_marker.jpg"
RIGHT_MARKER_PATH = r"C:\KODINGAN\db_manukashop\images\kotak\right_marker.jpg"
OUTPUT_DIR = r"\\100.89.33.56\Data Dari Noval\ORDERAN_2025\.noteFile"

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_json_data(id_input):
    """
    Mengambil data JSON berdasarkan ID input
    
    Args:
        id_input (str): ID yang akan dicari dalam file JSON
        
    Returns:
        dict: Data JSON jika ditemukan, None jika tidak
    """
    # Ekstrak pola ID jika merupakan bagian dari string yang lebih panjang
    id_pattern = r'(\d{4}-\d{5})'
    match = re.search(id_pattern, id_input)
    
    if match:
        id_text = match.group(1)
    else:
        id_text = id_input
    
    # Cari ID dalam file JSON
    for filename in os.listdir(JSON_DIR):
        if filename.endswith('.json'):
            file_path = os.path.join(JSON_DIR, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Periksa apakah JSON ini berisi ID yang dicari
                    if id_text in str(data):
                        return data
            except Exception as e:
                print(f"Error membaca {filename}: {e}")
    
    return None

def get_header_text(note_text):
    """
    Ekstrak teks header dari catatan
    
    Args:
        note_text (str): Teks catatan
        
    Returns:
        str: Teks header yang diekstrak
    """
    # Implementasi sederhana - dalam skenario nyata, ini mungkin lebih kompleks
    return note_text

def create_number_banner(text_str, output_path=None, from_note=False): 
    """
    Membuat banner dengan nomor ID dan kotak di sekitarnya
    
    Args:
        text_str (str): Teks yang berisi ID atau teks lengkap
        output_path (str, optional): Path untuk menyimpan output. Default None
        from_note (bool, optional): Flag apakah teks berasal dari note. Default False
    
    Returns:
        PIL.Image: Gambar banner yang telah dibuat
    """
    # Jika from_note=True, gunakan fungsi get_header_text untuk mendapatkan teks dari note
    if from_note:
        text_str = get_header_text(text_str)
    
    # Default output path jika tidak disediakan
    if output_path is None: 
        output_filename = f"header_{text_str.replace(' ', '_').replace('/', '_')[:30]}.png"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # Load marker images 
    left_img = Image.open(LEFT_MARKER_PATH).convert("RGBA") 
    right_img = Image.open(RIGHT_MARKER_PATH).convert("RGBA") 

    # Cek apakah input adalah teks lengkap dengan ID atau hanya ID
    id_pattern = r'(\d{4}-\d{5})'
    match = re.search(id_pattern, text_str)
    
    if match:
        # Jika input adalah teks lengkap dengan ID
        id_text = match.group(1)
        
        # Tambahkan spasi di sekitar ID dalam teks asli
        id_start_pos = text_str.find(id_text)
        id_end_pos = id_start_pos + len(id_text)
        
        # Buat teks baru dengan spasi di sekitar ID
        spaced_text = text_str[:id_start_pos] + "     " + id_text + "     " + text_str[id_end_pos:]
        
        # Font setup 
        font_size = 60 
        try: 
            font = ImageFont.truetype("arial.ttf", font_size) 
        except IOError: 
            font = ImageFont.load_default() 
        
        # Measure text size
        dummy_img = Image.new("RGBA", (1, 1)) 
        draw = ImageDraw.Draw(dummy_img) 
        
        # Ukur lebar teks lengkap dengan spasi
        bbox_full = draw.textbbox((0, 0), spaced_text, font=font) 
        full_width = bbox_full[2] - bbox_full[0] 
        full_height = bbox_full[3] - bbox_full[1]
        
        # Ukur lebar teks ID
        bbox_id = draw.textbbox((0, 0), id_text, font=font) 
        id_width = bbox_id[2] - bbox_id[0] 
        id_height = bbox_id[3] - bbox_id[1]
        
        # Padding dan spacing
        padding = 20
        spacing = 10  # Mengurangi spacing karena sudah ada spasi di teks
        
        # Hitung total lebar dan tinggi
        total_width = full_width + left_img.width + right_img.width + 2 * spacing + 2 * padding
        total_height = max(full_height, left_img.height, right_img.height) + 2 * padding
        
        # Buat canvas dengan background putih
        canvas = Image.new("RGBA", (total_width, total_height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        
        # Posisi vertikal tengah
        y_center = total_height // 2
        
        # Cari posisi ID dalam teks dengan spasi
        id_with_spaces = "     " + id_text + "     "
        id_start_pos = spaced_text.find(id_with_spaces)
        
        # Bagian teks sebelum ID dengan spasi
        pre_text = spaced_text[:id_start_pos]
        if pre_text:
            bbox_pre = draw.textbbox((0, 0), pre_text, font=font)
            pre_width = bbox_pre[2] - bbox_pre[0]
        else:
            pre_width = 0
        
        # Tulis teks lengkap dengan spasi (warna merah)
        text_x = padding
        text_y = y_center - full_height // 2
        draw.text((text_x, text_y), spaced_text, fill=(255, 0, 0), font=font)
        
        # Hitung posisi kotak kiri (tepat sebelum ID dengan spasi)
        left_box_x = text_x + pre_width
        left_box_y = y_center - left_img.height // 2
        
        # Hitung posisi kotak kanan (tepat setelah ID dengan spasi)
        right_box_x = left_box_x + bbox_id[2] - bbox_id[0] + 10 * spacing
        right_box_y = y_center - right_img.height // 2
        
        # Paste kotak kiri dan kanan
        canvas.paste(left_img, (int(left_box_x), int(left_box_y)), left_img)
        canvas.paste(right_img, (int(right_box_x), int(right_box_y)), right_img)
        
        # Simpan hasil
        canvas.save(output_path)
        print(f"✅ Banner saved to: {output_path}")
        return canvas, output_path
    else:
        # Jika input hanya ID, gunakan sebagai ID
        # Font setup 
        font_size = 60 
        try: 
            font = ImageFont.truetype("arial.ttf", font_size) 
        except IOError: 
            font = ImageFont.load_default() 
        
        # Measure text size
        dummy_img = Image.new("RGBA", (1, 1)) 
        draw = ImageDraw.Draw(dummy_img) 
        
        # Ukur lebar teks ID
        bbox = draw.textbbox((0, 0), text_str, font=font) 
        id_width = bbox[2] - bbox[0] 
        id_height = bbox[3] - bbox[1] 
        
        # Padding dan spacing
        padding = 20
        spacing = 10
        
        # Hitung total lebar dan tinggi
        total_width = left_img.width + spacing + id_width + spacing + right_img.width + 2 * padding
        total_height = max(left_img.height, id_height, right_img.height) + 2 * padding
        
        # Buat canvas dengan background putih
        canvas = Image.new("RGBA", (total_width, total_height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        
        # Posisi vertikal tengah
        y_center = total_height // 2
        
        # Paste kotak kiri
        left_x = padding
        left_y = y_center - left_img.height // 2
        canvas.paste(left_img, (left_x, left_y), left_img)
        
        # Tulis ID
        text_x = left_x + left_img.width + spacing
        text_y = y_center - id_height // 2
        draw.text((text_x, text_y), text_str, fill=(0, 0, 0), font=font)
        
        # Paste kotak kanan
        right_x = text_x + id_width + spacing
        right_y = y_center - right_img.height // 2
        canvas.paste(right_img, (right_x, right_y), right_img)
        
        # Simpan hasil
        canvas.save(output_path)
        print(f"✅ Banner saved to: {output_path}")
        return canvas, output_path

@design_header_bp.route('/generate', methods=['POST', 'OPTIONS'])
def generate_header():
    """
    Endpoint untuk menghasilkan banner header dari ID atau catatan
    """
    # Handle OPTIONS request untuk CORS
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.json
        
        if not data:
            return jsonify({"error": "Tidak ada data yang diberikan"}), 400
        
        # Dapatkan ID atau teks catatan
        id_input = data.get('id')
        
        if not id_input:
            return jsonify({"error": "Parameter 'id' harus disediakan"}), 400
        
        # Ambil data dari table_input_order untuk mendapatkan produk dan qty
        import sys
        import os
        
        # Tambahkan path ke direktori parent untuk mengimpor db.py
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from db import get_db_connection
        
        try:
            # Gunakan fungsi get_db_connection dari db.py
            connection = get_db_connection()
            
            cursor = connection.cursor(dictionary=True)
            # Query untuk mendapatkan data dari table_input_order
            query = """
                SELECT tio.id_input, tio.qty, tio.nama_ket
                FROM table_input_order tio
                WHERE tio.id_input = %s
            """
            cursor.execute(query, (id_input,))
            order_data = cursor.fetchone()
            
            if order_data:
                qty = str(order_data.get('qty', '1'))
                nama_ket = order_data.get('nama_ket', '')
                
                # Ekstrak informasi Produk dari nama_ket jika ada
                produk_info = "Unknown"
                if nama_ket:
                    # Cari pola "Produk : XXXX" dalam nama_ket
                    import re
                    produk_match = re.search(r'Produk\s*:\s*([^\n]+)', nama_ket)
                    if produk_match:
                        produk_info = produk_match.group(1).strip()
                    else:
                        # Jika tidak ditemukan, coba cari pola Type
                        type_match = re.search(r'Type\s*:\s*([^\n]+)', nama_ket)
                        if type_match:
                            produk_info = type_match.group(1).strip()
                        else:
                            # Jika masih tidak ditemukan, coba cari pola lain yang umum
                            sisi_match = re.search(r'SISI\s+([^\n,]+)', nama_ket)
                            if sisi_match:
                                produk_info = sisi_match.group(0).strip()
                
                # Format note dengan format yang diminta: {id_input} ({produk_info}), {qty} PCS
                note_text = f"{id_input} ({produk_info}), {qty} PCS"
                print(f"✅ Data ditemukan: {note_text}")
            else:
                # Jika data tidak ditemukan, gunakan ID sebagai note
                note_text = id_input
                print(f"⚠️ Data tidak ditemukan untuk ID: {id_input}")
            
            cursor.close()
            connection.close()
            
        except Exception as db_error:
            print(f"❌ Database error: {str(db_error)}")
            # Jika terjadi error, coba dapatkan catatan dari JSON jika ada
            json_data = get_json_data(id_input)
            
            if json_data:
                note_text = json_data.get('note')
                if not note_text:
                    note_text = id_input
            else:
                note_text = id_input
        
        # Buat JSON header dengan format {id_input}_header.json
        json_folder = "C:\\KODINGAN\\db_manukashop\\images\\jsonCode"
        os.makedirs(json_folder, exist_ok=True)
        header_json_filename = "header.json"  # Nama file tetap untuk selalu ditimpa
        header_json_path = os.path.join(json_folder, header_json_filename)
        
        # Buat data JSON header
        header_data = {
            "note": note_text
        }
        
        # Simpan file JSON header
        with open(header_json_path, 'w') as json_file:
            json.dump(header_data, json_file, indent=2)
        
        print(f"✅ Header JSON created: {header_json_path}")
        
        # Hasilkan nama file unik untuk header image
        id_pattern = r'(\d{4}-\d{5})'
        match = re.search(id_pattern, note_text)
        
        if match:
            id_text = match.group(1)
            filename = f"header_{id_text}.png"
        else:
            filename = f"header_{id_input.replace(' ', '_').replace('/', '_')[:30]}.png"
        
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        # Buat banner
        _, output_path = create_number_banner(note_text, output_path, from_note=True)
        
        # Kembalikan respons sukses dengan path file
        return jsonify({
            "success": True,
            "message": f"Header JSON dan banner berhasil dibuat (ID: {id_input})",
            "file_path": output_path,
            "filename": filename,
            "json_path": header_json_path,
            "json_filename": header_json_filename,
            "note_text": note_text
        }), 200
        
    except Exception as e:
        print(f"❌ Error in generate_header: {str(e)}")
        return jsonify({"error": str(e)}), 500

@design_header_bp.route('/download/<filename>', methods=['GET'])
def download_header(filename):
    """
    Endpoint untuk mengunduh header yang dihasilkan
    """
    try:
        file_path = os.path.join(OUTPUT_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({"error": "File tidak ditemukan"}), 404
            
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500