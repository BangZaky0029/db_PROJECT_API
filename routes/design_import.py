import json
import os
import re
import requests
from flask import Blueprint, request, jsonify, current_app

design_import_bp = Blueprint('design_import', __name__)

@design_import_bp.route('/import-design-json', methods=['POST'])
def import_design_json():
    """
    Import design JSON file and send it to the image processing API
    
    Expected JSON payload:
    {
        "id_input": "1025-00014",  # ID yang akan digunakan untuk mencari file JSON yang sudah dibuat oleh design_json.py
        "font_color": "#FF0000",    # Optional: Custom font color (default: dari file JSON)
        "header_font_size": 35,     # Optional: Custom header font size (default: dari file JSON)
        "nama_font_size": 200       # Optional: Custom nama font size (default: dari file JSON)
    }
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Get parameters from request
        id_input = data.get('id_input')
        if not id_input:
            return jsonify({"error": "id_input is required"}), 400
        
        # Define the JSON folder path
        json_folder = "C:\\KODINGAN\\db_manukashop\\images\\jsonCode"
        
        # Path ke file JSON yang sudah dibuat oleh design_json.py
        json_path = os.path.join(json_folder, "design.json")
        
        # Periksa apakah file JSON ada
        if not os.path.exists(json_path):
            return jsonify({"error": f"File JSON tidak ditemukan: {json_path}. Pastikan file JSON sudah dibuat dengan design_json.py"}), 404
        
        # Baca file JSON yang sudah ada
        try:
            with open(json_path, 'r') as file:
                design_data = json.load(file)
                print(f"INFO: Menggunakan file JSON yang sudah dibuat oleh design_json.py: {json_path}")
        except Exception as e:
            return jsonify({"error": f"Gagal membaca file JSON: {str(e)}"}), 500
        
        # Update note dengan id_input yang baru
        if "note" in design_data:
            # Ekstrak ID dari note yang ada dan ganti dengan id_input baru
            design_data["note"] = re.sub(r'\d{4}-\d{5}', id_input, design_data["note"])
            
        # Check if custom font parameters are provided in the request
        font_color = data.get('font_color')
        header_font_size = data.get('header_font_size')
        nama_font_size = data.get('nama_font_size')
        
        # Update design_data with custom values if provided
        if font_color:
            design_data['font_color'] = font_color
        if header_font_size:
            design_data['header_font_size'] = header_font_size
        if nama_font_size:
            design_data['nama_font_size'] = nama_font_size
        
        # Define the API endpoint
        # JANGAN DIPERBAHARUI MENJADI ENDPOINT INI....!!!!
        api_endpoint = "http://100.124.58.32:5001/api/design/create-multiple"
        
        # Send the JSON data to the API
        response = requests.post(
            api_endpoint,
            json=design_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Check if the request was successful (200 OK or 201 Created)
        if response.status_code == 200 or response.status_code == 201:
            try:
                api_response = response.json()
                # Jika ada pesan sukses dalam response
                if "Berhasil membuat" in str(api_response.get('error', '')):
                    return jsonify({
                        "success": True,
                        "message": api_response.get('error', 'Design imported and processed successfully'),
                        "status_code": 200
                    }), 200
                else:
                    return jsonify({
                        "success": True,
                        "message": "Design imported and processed successfully",
                        "api_response": api_response,
                        "status_code": 200
                    }), 200
            except Exception as e:
                print(f"ERROR parsing response: {str(e)}")
                return jsonify({
                    "success": True,
                    "message": "Design imported and processed successfully",
                    "response_text": response.text,
                    "status_code": 200
                }), 200
        else:
            # If the API request failed, return the error
            try:
                error_data = response.json()
                error_message = error_data.get('message', 'Unknown error')
            except:
                error_message = f"API request failed with status code {response.status_code}"
            
            return jsonify({
                "success": False,
                "message": "Failed to process design",
                "error": error_message,
                "status_code": response.status_code
            }), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@design_import_bp.route('/list-design-json', methods=['GET'])
def list_design_json():
    """List all available design JSON files"""
    try:
        # Define the JSON folder path
        json_folder = "C:\\KODINGAN\\db_manukashop\\images\\jsonCode"
        
        # Check if folder exists
        if not os.path.exists(json_folder):
            return jsonify({
                "success": False,
                "message": "JSON folder not found"
            }), 404
        
        # Get all JSON files in the folder
        json_files = [f for f in os.listdir(json_folder) if f.endswith('_design.json')]
        
        # Extract id_input from filenames
        designs = []
        for filename in json_files:
            # Extract id_input (e.g., "0925-00826" from "0925-00826_design.json")
            id_input = filename.replace('_design.json', '')
            
            # Get file path and creation time
            file_path = os.path.join(json_folder, filename)
            creation_time = os.path.getctime(file_path)
            
            designs.append({
                "id_input": id_input,
                "filename": filename,
                "file_path": file_path,
                "creation_time": creation_time
            })
        
        # Sort by creation time (newest first)
        designs.sort(key=lambda x: x['creation_time'], reverse=True)
        
        return jsonify({
            "success": True,
            "count": len(designs),
            "designs": designs
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500