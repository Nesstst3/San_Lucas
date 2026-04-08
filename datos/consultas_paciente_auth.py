from datos.conexion import obtener_conexion
from datetime import datetime, time, timedelta


def obtener_cuenta_paciente_por_usuario(usuario):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT
            cp.id_cuenta_paciente,
            cp.id_paciente,
            cp.usuario,
            cp.contrasena,
            cp.activo,
            cp.debe_cambiar_password,
            p.nombre,
            p.apellido_paterno,
            p.apellido_materno,
            p.correo,
            p.numero_expediente
        FROM cuentas_paciente cp
        INNER JOIN pacientes p ON cp.id_paciente = p.id_paciente
        WHERE cp.usuario = %s
        LIMIT 1
    """
    cursor.execute(query, (usuario,))
    cuenta = cursor.fetchone()

    cursor.close()
    conexion.close()

    return cuenta


def obtener_cuenta_paciente_por_id(id_cuenta_paciente):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT
            cp.id_cuenta_paciente,
            cp.id_paciente,
            cp.usuario,
            cp.contrasena,
            cp.activo,
            cp.debe_cambiar_password,
            p.nombre,
            p.apellido_paterno,
            p.apellido_materno,
            p.correo,
            p.numero_expediente,
            p.telefono,
            p.sexo,
            p.fecha_nacimiento
        FROM cuentas_paciente cp
        INNER JOIN pacientes p ON cp.id_paciente = p.id_paciente
        WHERE cp.id_cuenta_paciente = %s
        LIMIT 1
    """

    cursor.execute(query, (id_cuenta_paciente,))
    cuenta = cursor.fetchone()
    cursor.close()
    conexion.close()
    return cuenta


def actualizar_password_paciente(id_cuenta_paciente, nuevo_hash):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        query = """
            UPDATE cuentas_paciente
            SET contrasena = %s,
                debe_cambiar_password = 0,
                ultimo_acceso = NOW()
            WHERE id_cuenta_paciente = %s
        """
        cursor.execute(query, (nuevo_hash, id_cuenta_paciente))
        conexion.commit()
        return True
    except Exception as e:
        conexion.rollback()
        print("Error al actualizar password paciente:", e)
        return False
    finally:
        cursor.close()
        conexion.close()


def actualizar_ultimo_acceso_paciente(id_cuenta_paciente):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        query = """
            UPDATE cuentas_paciente
            SET ultimo_acceso = NOW()
            WHERE id_cuenta_paciente = %s
        """
        cursor.execute(query, (id_cuenta_paciente,))
        conexion.commit()
        return True
    except Exception as e:
        conexion.rollback()
        print("Error al actualizar último acceso:", e)
        return False
    finally:
        cursor.close()
        conexion.close()

def obtener_proximas_citas_paciente(id_paciente):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT
            c.id_cita,
            c.folio,
            c.fecha,
            TIME_FORMAT(c.hora, '%H:%i') AS hora,
            c.motivo,
            d.nombre AS doctor_nombre,
            d.apellido_paterno AS doctor_apellido,
            CASE
                WHEN d.id_especialidad = 1 THEN 'Nutriología'
                WHEN d.id_especialidad = 2 THEN 'Dermatología'
                WHEN d.id_especialidad = 3 THEN 'Obstetricia'
                WHEN d.id_especialidad = 4 THEN 'Psicología'
                ELSE 'Sin especialidad'
            END AS especialidad
        FROM citas c
        INNER JOIN doctores d ON c.id_doctor = d.id_doctor
        WHERE c.id_paciente = %s
          AND (
                c.fecha > CURDATE()
                OR (c.fecha = CURDATE() AND c.hora >= CURTIME())
          )
        ORDER BY c.fecha ASC, c.hora ASC
    """
    cursor.execute(query, (id_paciente,))
    citas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return citas


def obtener_resumen_citas_paciente(id_paciente):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT
            COUNT(*) AS total_proximas
        FROM citas
        WHERE id_paciente = %s
          AND (
                fecha > CURDATE()
                OR (fecha = CURDATE() AND hora >= CURTIME())
          )
    """
    cursor.execute(query, (id_paciente,))
    resumen = cursor.fetchone()

    cursor.close()
    conexion.close()

    return resumen

def obtener_historial_paciente(id_paciente):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT
            c.id_cita,
            c.folio,
            DATE_FORMAT(c.fecha, '%d/%m/%Y') AS fecha,
            TIME_FORMAT(c.hora, '%H:%i') AS hora,
            c.motivo,
            d.nombre AS doctor_nombre,
            d.apellido_paterno AS doctor_apellido,
            CASE
                WHEN d.id_especialidad = 1 THEN 'Nutriología'
                WHEN d.id_especialidad = 2 THEN 'Dermatología'
                WHEN d.id_especialidad = 3 THEN 'Obstetricia'
                WHEN d.id_especialidad = 4 THEN 'Psicología'
                ELSE 'Sin especialidad'
            END AS especialidad,
            cm.id_consulta,
            cm.diagnostico,
            cm.tratamiento,
            cm.observaciones
        FROM consultas_medicas cm
        INNER JOIN citas c ON cm.id_cita = c.id_cita
        INNER JOIN doctores d ON c.id_doctor = d.id_doctor
        WHERE c.id_paciente = %s
        ORDER BY c.fecha DESC, c.hora DESC
    """

    cursor.execute(query, (id_paciente,))
    historial = cursor.fetchall()

    cursor.close()
    conexion.close()
    return historial

def obtener_recetas_paciente(id_paciente):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT
            c.id_cita,
            c.folio,
            DATE_FORMAT(c.fecha, '%d/%m/%Y') AS fecha,
            TIME_FORMAT(c.hora, '%H:%i') AS hora,
            c.motivo,
            d.nombre AS doctor_nombre,
            d.apellido_paterno AS doctor_apellido,
            CASE
                WHEN d.id_especialidad = 1 THEN 'Nutriología'
                WHEN d.id_especialidad = 2 THEN 'Dermatología'
                WHEN d.id_especialidad = 3 THEN 'Obstetricia'
                WHEN d.id_especialidad = 4 THEN 'Psicología'
                ELSE 'Sin especialidad'
            END AS especialidad,
            cm.id_consulta,
            cm.diagnostico,
            cm.tratamiento,
            cm.observaciones
        FROM consultas_medicas cm
        INNER JOIN citas c ON cm.id_cita = c.id_cita
        INNER JOIN doctores d ON c.id_doctor = d.id_doctor
        WHERE c.id_paciente = %s
          AND cm.tratamiento IS NOT NULL
          AND TRIM(cm.tratamiento) <> ''
        ORDER BY c.fecha DESC, c.hora DESC
    """

    cursor.execute(query, (id_paciente,))
    recetas = cursor.fetchall()

    cursor.close()
    conexion.close()
    return recetas

def actualizar_fecha_nacimiento_paciente(id_paciente, fecha_nacimiento):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        query = """
            UPDATE pacientes
            SET fecha_nacimiento = %s
            WHERE id_paciente = %s
        """
        cursor.execute(query, (fecha_nacimiento, id_paciente))
        conexion.commit()
        return cursor.rowcount > 0
    except Exception:
        conexion.rollback()
        return False
    finally:
        cursor.close()
        conexion.close()

def cancelar_cita_paciente(id_cita, id_paciente):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        query_cita = """
            SELECT id_cita, fecha, hora
            FROM citas
            WHERE id_cita = %s
              AND id_paciente = %s
            LIMIT 1
        """
        cursor.execute(query_cita, (id_cita, id_paciente))
        cita = cursor.fetchone()

        if not cita:
            return False, "La cita no existe o no pertenece a tu cuenta."

        fecha_cita = cita["fecha"]
        hora_cita = cita["hora"]

        if hasattr(hora_cita, "total_seconds"):
            total_segundos = int(hora_cita.total_seconds())
            horas = total_segundos // 3600
            minutos = (total_segundos % 3600) // 60
            hora_cita = time(horas, minutos)
        elif isinstance(hora_cita, str):
            hora_cita = datetime.strptime(hora_cita[:5], "%H:%M").time()

        fecha_hora_cita = datetime.combine(fecha_cita, hora_cita)
        ahora = datetime.now()

        if fecha_hora_cita - ahora < timedelta(hours=24):
            return False, "Solo puedes cancelar una cita con al menos 24 horas de anticipación."

        query_delete = """
            DELETE FROM citas
            WHERE id_cita = %s
              AND id_paciente = %s
        """
        cursor.execute(query_delete, (id_cita, id_paciente))
        conexion.commit()

        if cursor.rowcount == 0:
            return False, "No se pudo cancelar la cita."

        return True, None

    except Exception as e:
        conexion.rollback()
        print("Error al cancelar cita del paciente:", e)
        return False, "Ocurrió un error al cancelar la cita."

    finally:
        cursor.close()
        conexion.close()

def obtener_cita_paciente_por_id(id_cita, id_paciente):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    query = """
        SELECT
            c.id_cita,
            c.id_paciente,
            c.id_doctor,
            DATE_FORMAT(c.fecha, '%Y-%m-%d') AS fecha_form,
            TIME_FORMAT(c.hora, '%H:%i') AS hora_form,
            DATE_FORMAT(c.fecha, '%d/%m/%Y') AS fecha_mostrar,
            TIME_FORMAT(c.hora, '%H:%i') AS hora_mostrar,
            c.motivo,
            d.nombre AS doctor_nombre,
            d.apellido_paterno AS doctor_apellido,
            CASE
                WHEN d.id_especialidad = 1 THEN 'Nutriología'
                WHEN d.id_especialidad = 2 THEN 'Dermatología'
                WHEN d.id_especialidad = 3 THEN 'Obstetricia'
                WHEN d.id_especialidad = 4 THEN 'Psicología'
                ELSE 'Sin especialidad'
            END AS especialidad
        FROM citas c
        INNER JOIN doctores d ON c.id_doctor = d.id_doctor
        WHERE c.id_cita = %s
          AND c.id_paciente = %s
        LIMIT 1
    """

    cursor.execute(query, (id_cita, id_paciente))
    cita = cursor.fetchone()

    cursor.close()
    conexion.close()
    return cita


def reagendar_cita_paciente(id_cita, id_paciente, id_doctor, fecha, hora, motivo):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        hora_normalizada = hora[:5]

        query_valida = """
            SELECT COUNT(*) AS total
            FROM citas
            WHERE id_cita = %s
              AND id_paciente = %s
              AND (
                    fecha > CURDATE()
                    OR (fecha = CURDATE() AND hora >= CURTIME())
                  )
        """
        cursor.execute(query_valida, (id_cita, id_paciente))
        valida = cursor.fetchone()

        if not valida or int(valida["total"]) == 0:
            return False, "La cita ya no está disponible para reagendar."

        query_conflicto = """
            SELECT COUNT(*) AS total
            FROM citas
            WHERE id_doctor = %s
              AND fecha = %s
              AND TIME_FORMAT(hora, '%%H:%%i') = %s
              AND id_cita <> %s
        """
        cursor.execute(query_conflicto, (id_doctor, fecha, hora_normalizada, id_cita))
        conflicto = cursor.fetchone()

        if conflicto and int(conflicto["total"]) > 0:
            return False, "Ese horario ya no está disponible para el médico seleccionado."

        query_update = """
            UPDATE citas
            SET id_doctor = %s,
                fecha = %s,
                hora = %s,
                motivo = %s
            WHERE id_cita = %s
              AND id_paciente = %s
        """
        cursor.execute(query_update, (id_doctor, fecha, hora_normalizada, motivo, id_cita, id_paciente))
        conexion.commit()

        return True, None

    except Exception as e:
        conexion.rollback()
        print("Error al reagendar cita del paciente:", e)
        return False, str(e)

    finally:
        cursor.close()
        conexion.close()

def obtener_horas_ocupadas_para_paciente(id_doctor, fecha, id_cita_excluir=None):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        query = """
            SELECT TIME_FORMAT(hora, '%H:%i') AS hora
            FROM citas
            WHERE id_doctor = %s
              AND fecha = %s
        """
        params = [id_doctor, fecha]

        if id_cita_excluir:
            query += " AND id_cita <> %s"
            params.append(id_cita_excluir)

        query += " ORDER BY hora"

        cursor.execute(query, tuple(params))
        resultados = cursor.fetchall()

        horas = []
        for fila in resultados:
            if isinstance(fila, tuple):
                horas.append(fila[0])
            else:
                horas.append(fila["hora"])

        return horas

    except Exception as e:
        print("Error al obtener horas ocupadas:", e)
        return []

    finally:
        cursor.close()
        conexion.close()