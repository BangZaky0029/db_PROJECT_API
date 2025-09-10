from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
from routes import api_bp
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_url_path='', 
            static_folder=os.path.abspath(r'c:\KODINGAN\db_manukashop\db_WEB-SERVER'))

CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
}, supports_credentials=True)

@app.route('/')
def home():
    client_ip = request.remote_addr
    logger.info(f"Access from IP: {client_ip}")
    return send_from_directory(app.static_folder, 'mainWEB.html')

@app.route('/<path:path>')
def serve_static(path):
    client_ip = request.remote_addr
    logger.info(f"Static file request from IP: {client_ip} for path: {path}")
    return send_from_directory(app.static_folder, path)

app.register_blueprint(api_bp)

if __name__ == '__main__':
    try:
        logger.info("Starting server... Web accessible from all IPs on port 5000")
        logger.info(f"Static files served from: {app.static_folder}")
        app.run(
            host='0.0.0.0',  # Changed to allow all IP access
            port=5000,
            debug=False,
            threaded=True,
            use_reloader=False  # Disable auto-reloader to prevent refresh
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
