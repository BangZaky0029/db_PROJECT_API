import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="100.124.58.32",
        user="root",
        password="/BangZ@ky0029/",  # Password baru
        database="db_mnk",
        autocommit=True
    )
    return conn
