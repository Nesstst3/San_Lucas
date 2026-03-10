from datos.conexion import obtener_conexion


def autenticar_usuario(correo, contrasena):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT id_usuario, correo, rol, id_doctor
        FROM usuarios
        WHERE correo = %s AND contrasena = %s AND activo = 1
        LIMIT 1
    """
    cursor.execute(sql, (correo, contrasena))
    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    return usuario