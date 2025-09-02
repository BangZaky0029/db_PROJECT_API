 
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from db import get_db_connection
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    @staticmethod
    def get_pending_orders():
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                        SELECT 
                            p.id_input, 
                            a.nama AS nama_admin,
                            pr.nama_produk,
                            p.platform,
                            DATE(p.timestamp) AS inputan_masuk,
                            p.deadline,
                            p.qty AS Jumlah_pcs,
                            p.status_print,
                            p.status_produksi,
                            a.ID AS id_admin
                        FROM table_pesanan p
                        JOIN table_produk pr ON p.id_produk = pr.id_produk
                        JOIN table_admin a ON p.id_admin = a.ID
                        JOIN table_input_order io ON p.id_input = io.id_input
                        WHERE 
                            p.deadline BETWEEN '2025-03-01' AND '2025-12-31'  -- Filter deadline hanya di bulan Maret
                            AND p.status_produksi = '-'  -- Hanya pesanan yang belum diproduksi
                        ORDER BY p.deadline ASC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
            
    @staticmethod
    def test_connection():
        """Test database connection and return sample data"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Test with a simpler query
            cursor.execute("SELECT COUNT(*) as count FROM table_pesanan")
            count_result = cursor.fetchone()
            
            # Get a sample of orders regardless of status
            cursor.execute("""
                SELECT p.id_input, a.nama AS nama_admin, pr.nama_produk, 
                       p.deadline, p.status_print, p.status_produksi
                FROM table_pesanan p
                JOIN table_produk pr ON p.id_produk = pr.id_produk
                JOIN table_admin a ON p.id_admin = a.ID
                LIMIT 5
            """)
            sample_orders = cursor.fetchall()
            
            return {
                "connection": "success",
                "order_count": count_result['count'] if count_result else 0,
                "sample_orders": sample_orders
            }
        except Exception as e:
            logger.error(f"Test connection error: {str(e)}")
            return {
                "connection": "error",
                "message": str(e)
            }
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()