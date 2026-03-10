from datos.conexion import obtener_conexion


def obtener_doctores_panel():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    sql = """
        SELECT 
            d.id_doctor,
            d.nombre,
            d.apellido_paterno,
            d.apellido_materno,
            e.nombre AS especialidad
        FROM doctores d
        INNER JOIN especialidades e
            ON d.id_especialidad = e.id_especialidad
        ORDER BY d.nombre, d.apellido_paterno
    """

    cursor.execute(sql)
    doctores = cursor.fetchall()

    cursor.close()
    conexion.close()

    return doctores


def obtener_citas_por_doctor_y_filtro(id_doctor, filtro):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    if filtro == "proximas":
        sql = """
            SELECT 
                c.folio,
                c.fecha,
                TIME_FORMAT(c.hora, '%H:%i') AS hora,
                c.motivo,
                p.numero_expediente,
                p.nombre,
                p.apellido_paterno,
                p.apellido_materno,
                p.telefono,
                p.correo
            FROM citas c
            INNER JOIN pacientes p ON c.id_paciente = p.id_paciente
            WHERE c.id_doctor = %s
              AND (c.fecha > CURDATE() OR (c.fecha = CURDATE() AND c.hora >= CURTIME()))
            ORDER BY c.fecha ASC, c.hora ASC
        """
    elif filtro == "pasadas":
        sql = """
            SELECT 
                c.folio,
                c.fecha,
                TIME_FORMAT(c.hora, '%H:%i') AS hora,
                c.motivo,
                p.numero_expediente,
                p.nombre,
                p.apellido_paterno,
                p.apellido_materno,
                p.telefono,
                p.correo
            FROM citas c
            INNER JOIN pacientes p ON c.id_paciente = p.id_paciente
            WHERE c.id_doctor = %s
              AND (c.fecha < CURDATE() OR (c.fecha = CURDATE() AND c.hora < CURTIME()))
            ORDER BY c.fecha DESC, c.hora DESC
        """
    elif filtro == "siguiente_mes":
        sql = """
            SELECT 
                c.folio,
                c.fecha,
                TIME_FORMAT(c.hora, '%H:%i') AS hora,
                c.motivo,
                p.numero_expediente,
                p.nombre,
                p.apellido_paterno,
                p.apellido_materno,
                p.telefono,
                p.correo
            FROM citas c
            INNER JOIN pacientes p ON c.id_paciente = p.id_paciente
            WHERE c.id_doctor = %s
              AND YEAR(c.fecha) = YEAR(DATE_ADD(CURDATE(), INTERVAL 1 MONTH))
              AND MONTH(c.fecha) = MONTH(DATE_ADD(CURDATE(), INTERVAL 1 MONTH))
            ORDER BY c.fecha ASC, c.hora ASC
        """
    else:
        sql = """
            SELECT 
                c.folio,
                c.fecha,
                TIME_FORMAT(c.hora, '%H:%i') AS hora,
                c.motivo,
                p.numero_expediente,
                p.nombre,
                p.apellido_paterno,
                p.apellido_materno,
                p.telefono,
                p.correo
            FROM citas c
            INNER JOIN pacientes p ON c.id_paciente = p.id_paciente
            WHERE c.id_doctor = %s
            ORDER BY c.fecha ASC, c.hora ASC
        """

    cursor.execute(sql, (id_doctor,))
    citas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return citas