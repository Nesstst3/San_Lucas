import calendar
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

from datos.consultas_paciente_auth import (
    obtener_cuenta_paciente_por_usuario,
    obtener_cuenta_paciente_por_id,
    actualizar_password_paciente,
    actualizar_ultimo_acceso_paciente,
    obtener_proximas_citas_paciente,
    obtener_resumen_citas_paciente,
    obtener_historial_paciente,
    obtener_recetas_paciente
)

paciente_auth = Blueprint("paciente_auth", __name__)

MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

DIAS_SEMANA_ES = ["L", "M", "M", "J", "V", "S", "D"]


def construir_calendario_paciente(proximas_citas):
    hoy = date.today()
    calendario = calendar.Calendar(firstweekday=0)  # Lunes

    semanas_crudas = calendario.monthdayscalendar(hoy.year, hoy.month)
    dias_con_cita = set()

    for cita in proximas_citas:
        fecha_cita = cita.get("fecha")

        if isinstance(fecha_cita, datetime):
            fecha_cita = fecha_cita.date()

        elif isinstance(fecha_cita, str):
            formatos = ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S")
            fecha_parseada = None

            for formato in formatos:
                try:
                    fecha_parseada = datetime.strptime(fecha_cita, formato).date()
                    break
                except ValueError:
                    continue

            if not fecha_parseada:
                continue

            fecha_cita = fecha_parseada

        if isinstance(fecha_cita, date):
            if fecha_cita.year == hoy.year and fecha_cita.month == hoy.month:
                dias_con_cita.add(fecha_cita.day)

    semanas = []
    for semana in semanas_crudas:
        fila = []
        for dia in semana:
            fila.append({
                "numero": dia if dia != 0 else "",
                "es_hoy": dia == hoy.day,
                "tiene_cita": dia in dias_con_cita if dia != 0 else False
            })
        semanas.append(fila)

    return {
        "mes": MESES_ES[hoy.month - 1],
        "anio": hoy.year,
        "hoy": hoy.day,
        "dias_semana": DIAS_SEMANA_ES,
        "semanas": semanas
    }


def paciente_logueado():
    return session.get("rol_paciente") == "paciente"


@paciente_auth.route("/paciente/login", methods=["GET", "POST"])
def login_paciente():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not usuario or not password:
            flash("Ingresa tu usuario y contraseña.", "error")
            return render_template("login_paciente.html")

        cuenta = obtener_cuenta_paciente_por_usuario(usuario)

        if not cuenta:
            flash("No se encontró una cuenta de paciente con esos datos.", "error")
            return render_template("login_paciente.html")

        if int(cuenta["activo"]) != 1:
            flash("Tu cuenta está inactiva. Comunícate con recepción.", "error")
            return render_template("login_paciente.html")

        if not check_password_hash(cuenta["contrasena"], password):
            flash("La contraseña es incorrecta.", "error")
            return render_template("login_paciente.html")

        session["id_cuenta_paciente"] = cuenta["id_cuenta_paciente"]
        session["id_paciente"] = cuenta["id_paciente"]
        session["rol_paciente"] = "paciente"
        session["nombre_paciente"] = f"{cuenta['nombre']} {cuenta['apellido_paterno']}"

        if int(cuenta["debe_cambiar_password"]) == 1:
            flash("Debes cambiar tu contraseña antes de continuar.", "error")
            return redirect(url_for("paciente_auth.cambiar_password_inicial"))

        actualizar_ultimo_acceso_paciente(cuenta["id_cuenta_paciente"])
        return redirect(url_for("paciente_auth.panel_paciente"))

    return render_template("login_paciente.html")


@paciente_auth.route("/paciente/cambiar-password", methods=["GET", "POST"])
def cambiar_password_inicial():
    if not paciente_logueado():
        return redirect(url_for("paciente_auth.login_paciente"))

    id_cuenta_paciente = session.get("id_cuenta_paciente")
    cuenta = obtener_cuenta_paciente_por_id(id_cuenta_paciente)

    if not cuenta:
        session.clear()
        return redirect(url_for("paciente_auth.login_paciente"))

    if request.method == "POST":
        actual = request.form.get("password_actual", "").strip()
        nueva = request.form.get("nueva_password", "").strip()
        confirmar = request.form.get("confirmar_password", "").strip()

        if not actual or not nueva or not confirmar:
            flash("Completa todos los campos.", "error")
            return render_template("cambiar_password_paciente.html", cuenta=cuenta)

        if not check_password_hash(cuenta["contrasena"], actual):
            flash("La contraseña actual no es correcta.", "error")
            return render_template("cambiar_password_paciente.html", cuenta=cuenta)

        if len(nueva) < 8:
            flash("La nueva contraseña debe tener al menos 8 caracteres.", "error")
            return render_template("cambiar_password_paciente.html", cuenta=cuenta)

        if nueva != confirmar:
            flash("Las contraseñas no coinciden.", "error")
            return render_template("cambiar_password_paciente.html", cuenta=cuenta)

        if actual == nueva:
            flash("La nueva contraseña no puede ser igual a la temporal.", "error")
            return render_template("cambiar_password_paciente.html", cuenta=cuenta)

        nuevo_hash = generate_password_hash(nueva)
        actualizado = actualizar_password_paciente(id_cuenta_paciente, nuevo_hash)

        if actualizado:
            session.clear()
            flash("Tu contraseña fue actualizada correctamente. Inicia sesión con tu nueva contraseña.", "success")
            return redirect(url_for("paciente_auth.login_paciente"))

        flash("No se pudo actualizar la contraseña.", "error")

    return render_template("cambiar_password_paciente.html", cuenta=cuenta)


@paciente_auth.route("/paciente/panel")
def panel_paciente():
    if not paciente_logueado():
        return redirect(url_for("paciente_auth.login_paciente"))

    id_cuenta_paciente = session.get("id_cuenta_paciente")
    cuenta = obtener_cuenta_paciente_por_id(id_cuenta_paciente)

    if not cuenta:
        session.clear()
        return redirect(url_for("paciente_auth.login_paciente"))

    if int(cuenta["debe_cambiar_password"]) == 1:
        return redirect(url_for("paciente_auth.cambiar_password_inicial"))

    proximas_citas = obtener_proximas_citas_paciente(cuenta["id_paciente"])
    resumen_citas = obtener_resumen_citas_paciente(cuenta["id_paciente"])

    historial_paciente = obtener_historial_paciente(cuenta["id_paciente"])
    total_historial = len(historial_paciente)
    ultima_consulta_historial = historial_paciente[0] if historial_paciente else None
    recetas_paciente = obtener_recetas_paciente(cuenta["id_paciente"])
    total_recetas = len(recetas_paciente)
    ultima_receta = recetas_paciente[0] if recetas_paciente else None

    proxima_cita = proximas_citas[0] if proximas_citas else None
    total_proximas = resumen_citas["total_proximas"] if resumen_citas else 0
    calendario_paciente = construir_calendario_paciente(proximas_citas)

    return render_template(
    "panel_paciente.html",
    cuenta=cuenta,
    proximas_citas=proximas_citas,
    proxima_cita=proxima_cita,
    total_proximas=total_proximas,
    calendario_paciente=calendario_paciente,
    historial_paciente=historial_paciente,
    total_historial=total_historial,
    ultima_consulta_historial=ultima_consulta_historial,
    recetas_paciente=recetas_paciente,
    total_recetas=total_recetas,
    ultima_receta=ultima_receta
)

@paciente_auth.route("/paciente/mis-citas")
def mis_citas_paciente():
    if not paciente_logueado():
        return redirect(url_for("paciente_auth.login_paciente"))

    id_cuenta_paciente = session.get("id_cuenta_paciente")
    cuenta = obtener_cuenta_paciente_por_id(id_cuenta_paciente)

    if not cuenta:
        session.clear()
        return redirect(url_for("paciente_auth.login_paciente"))

    if int(cuenta["debe_cambiar_password"]) == 1:
        return redirect(url_for("paciente_auth.cambiar_password_inicial"))

    proximas_citas = obtener_proximas_citas_paciente(cuenta["id_paciente"])
    resumen_citas = obtener_resumen_citas_paciente(cuenta["id_paciente"])
    total_proximas = resumen_citas["total_proximas"] if resumen_citas else 0

    return render_template(
        "mis_citas_paciente.html",
        cuenta=cuenta,
        proximas_citas=proximas_citas,
        total_proximas=total_proximas
    )

@paciente_auth.route("/paciente/historial")
def historial_paciente():
    if not paciente_logueado():
        return redirect(url_for("paciente_auth.login_paciente"))

    id_cuenta_paciente = session.get("id_cuenta_paciente")
    cuenta = obtener_cuenta_paciente_por_id(id_cuenta_paciente)

    if not cuenta:
        session.clear()
        return redirect(url_for("paciente_auth.login_paciente"))

    if int(cuenta["debe_cambiar_password"]) == 1:
        return redirect(url_for("paciente_auth.cambiar_password_inicial"))

    historial = obtener_historial_paciente(cuenta["id_paciente"])
    total_historial = len(historial)
    ultima_consulta = historial[0] if historial else None

    return render_template(
        "historial_paciente.html",
        cuenta=cuenta,
        historial=historial,
        total_historial=total_historial,
        ultima_consulta=ultima_consulta
    )

@paciente_auth.route("/paciente/recetas")
def recetas_paciente():
    if not paciente_logueado():
        return redirect(url_for("paciente_auth.login_paciente"))

    id_cuenta_paciente = session.get("id_cuenta_paciente")
    cuenta = obtener_cuenta_paciente_por_id(id_cuenta_paciente)

    if not cuenta:
        session.clear()
        return redirect(url_for("paciente_auth.login_paciente"))

    if int(cuenta["debe_cambiar_password"]) == 1:
        return redirect(url_for("paciente_auth.cambiar_password_inicial"))

    recetas = obtener_recetas_paciente(cuenta["id_paciente"])
    total_recetas = len(recetas)
    ultima_receta = recetas[0] if recetas else None

    return render_template(
        "recetas_paciente.html",
        cuenta=cuenta,
        recetas=recetas,
        total_recetas=total_recetas,
        ultima_receta=ultima_receta
    )

@paciente_auth.route("/paciente/logout")
def logout_paciente():
    session.pop("id_cuenta_paciente", None)
    session.pop("id_paciente", None)
    session.pop("rol_paciente", None)
    session.pop("nombre_paciente", None)
    return redirect(url_for("paciente_auth.login_paciente"))