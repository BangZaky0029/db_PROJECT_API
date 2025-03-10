import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="100.117.80.112",
        user="root",
        password="/BangZ@ky0029/",  # Password baru
        database="db_mnk",
        autocommit=True
    )
    return conn
