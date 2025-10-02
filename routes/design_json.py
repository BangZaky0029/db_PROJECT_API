import json
import re
import os
from flask import Blueprint, request, jsonify, send_file

design_json_bp = Blueprint('design_json', __name__)

@design_json_bp.route('/generate-design-json', methods=['POST'])
def generate_design_json():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Handle both direct fields and fields from nama_ket
        id_input = data.get('id_input')
        nama_ket = data.get('nama_ket')
        
        # Check if we're receiving the new JSON format with motifs array
        if 'motifs' in data and isinstance(data['motifs'], list) and len(data['motifs']) > 0:
            # New format - use direct fields from JSON exactly as provided
            nama_depan = data.get('nama_depan', '')
            nama_belakang = data.get('nama_belakang', '')
            note = data.get('note', '')  # Gunakan note persis seperti yang diberikan
            font_color = data.get('font_color', '#000000')
            header_font_size = data.get('header_font_size', 30)
            nama_font_size = data.get('nama_font_size', 180)
            
            # Get motif information from the first motif in the array
            first_motif = data['motifs'][0]
            motif_kode = first_motif.get('image_name', '')
            qty = first_motif.get('qty', 1)
            
            # Extract ID input from note if available (hanya untuk nama file)
            if note:
                id_match = re.search(r'\d{4}-\d{5}', note)
                if id_match:
                    id_input = id_match.group(0)
            
            # Create design data structure - gunakan nilai persis seperti yang diberikan
            design_data = {
                "nama_depan": nama_depan,
                "nama_belakang": nama_belakang,
                "note": note,  # Gunakan note persis seperti yang diberikan tanpa modifikasi
                "font_color": font_color,
                "header_font_size": header_font_size,
                "nama_font_size": nama_font_size,
                "motifs": [
                    {
                        "image_name": motif_kode,
                        "qty": qty
                    }
                ]
            }
            
        else:
            # Old format - parse from nama_ket
            if not id_input or not nama_ket:
                return jsonify({"error": "Missing required fields"}), 400
            
            qty = data.get('qty', 1)
            produk = data.get('produk', '')
            
            # Parse nama_ket untuk mendapatkan informasi yang dibutuhkan
            nama_depan = extract_field(nama_ket, r'Nama Depan\s+:\s*(.*?)(?:\r?\n|$)')
            nama_belakang = extract_field(nama_ket, r'Nama Belakang\s+:\s*(.*?)(?:\r?\n|$)')
            motif_kode = extract_field(nama_ket, r'Motif/Kode\s+:\s*(.*?)(?:\r?\n|$)')
            
            # Parse produk dari nama_ket jika tersedia
            parsed_produk = extract_field(nama_ket, r'Produk\s+:\s*(.*?)(?:\r?\n|$)')
            if parsed_produk:
                produk = parsed_produk
            
            # Buat note dengan format yang diminta
            note = f"{id_input} ({produk}), {qty} PCS"
            
            # Buat struktur JSON
            design_data = {
                "nama_depan": nama_depan,
                "nama_belakang": nama_belakang,
                "note": note,
                "font_color": "#000000",
                "header_font_size": 30,
                "nama_font_size": 180,
                "produk": produk,
                "motifs": [
                    {
                        "image_name": motif_kode,
                        "qty": qty
                    }
                ]
            }
        
        # Ensure we have an id_input for the filename only
        # This doesn't modify the note value in design_data, only extracts ID for filename
        if not id_input and 'note' in design_data:
            id_match = re.search(r'\d{4}-\d{5}', design_data['note'])
            if id_match:
                id_input = id_match.group(0)
            else:
                # Generate a timestamp-based ID if no ID is found
                from datetime import datetime
                id_input = datetime.now().strftime("GEN-%Y%m%d-%H%M%S")
        
        # Simpan ke file JSON di folder jsonCode dengan nama tetap
        json_filename = "design.json"  # Nama file tetap untuk selalu ditimpa
        json_folder = "C:\\KODINGAN\\db_manukashop\\images\\jsonCode"
        
        # Pastikan folder ada
        os.makedirs(json_folder, exist_ok=True)
        
        json_path = os.path.join(json_folder, json_filename)
        
        with open(json_path, 'w') as json_file:
            json.dump(design_data, json_file, indent=2)
        
        return jsonify({
            "success": True,
            "message": f"Design JSON created successfully (ID: {id_input})",
            "file_path": json_path,
            "data": design_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_field(text, pattern):
    """Extract field value using regex pattern"""
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return ""

@design_json_bp.route('/generate-header-json', methods=['POST'])
def generate_header_json():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get order ID
        id_input = data.get('id')
        if not id_input:
            return jsonify({"error": "Missing order ID"}), 400
        
        # Try to find existing design JSON file
        json_folder = "C:\\KODINGAN\\db_manukashop\\images\\jsonCode"
        design_json_path = os.path.join(json_folder, f"{id_input}_design.json")
        
        # If design JSON exists, extract note from it
        note = ""
        if os.path.exists(design_json_path):
            try:
                with open(design_json_path, 'r') as file:
                    design_data = json.load(file)
                    note = design_data.get('note', '')
            except Exception as e:
                return jsonify({"error": f"Error reading design JSON: {str(e)}"}), 500
        else:
            # If no design JSON, use the ID as note
            note = id_input
        
        # Create header JSON data
        header_data = {
            "note": note
        }
        
        # Save header JSON file dengan nama tetap
        header_json_filename = "header.json"  # Nama file tetap untuk selalu ditimpa
        os.makedirs(json_folder, exist_ok=True)
        header_json_path = os.path.join(json_folder, header_json_filename)
        
        with open(header_json_path, 'w') as json_file:
            json.dump(header_data, json_file, indent=2)
        
        return jsonify({
            "success": True,
            "message": f"Header JSON created successfully (ID: {id_input})",
            "file_path": header_json_path,
            "data": header_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500