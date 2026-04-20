import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="roundhouse.proxy.rlwy.net",
        port=21377,
        user="root",
        password="DXxZFGOAGNnKBOdZhqtqZAGCUCPqRiOG",
        database="final_project",
        connection_timeout=10
    )