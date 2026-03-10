from datos.conexion import obtener_conexion


def obtener_especialidades():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT id_especialidad, nombre, descripcion, imagen
        FROM especialidades
        ORDER BY id_especialidad
    """
    cursor.execute(sql)
    especialidades = cursor.fetchall()

    cursor.close()
    conexion.close()

    return especialidades


def obtener_doctores():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT 
            d.id_doctor,
            d.nombre,
            d.apellido_paterno,
            d.apellido_materno,
            d.imagen,
            e.nombre AS especialidad
        FROM doctores d
        INNER JOIN especialidades e
            ON d.id_especialidad = e.id_especialidad
        ORDER BY d.id_doctor
    """
    cursor.execute(sql)
    doctores = cursor.fetchall()

    cursor.close()
    conexion.close()

    return doctores