import mysql.connector

def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="pc1101OG*",
        database="clinica_san_lucas",
        port=3306
    )