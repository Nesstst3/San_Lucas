from flask import Blueprint, render_template, request, session, redirect, url_for
from datos.consultas_medico import (
    obtener_citas_del_medico,
    obtener_detalle_cita,
    guardar_consulta_completa,
    obtener_expediente_completo
)

medico = Blueprint("medico", __name__)


def acceso_medico():
    return session.get("rol") == "medico"


def obtener_id_medico_sesion():
    """
    Toma el id del médico desde la sesión.
    Soporta ambos nombres por si en auth guardaste:
    - id_doctor
    - id_usuario
    """
    return session.get("id_doctor") or session.get("id_usuario")


@medico.route("/dashboard")
def dashboard():
    if not acceso_medico():
        return redirect(url_for("auth.login"))

    id_doctor = obtener_id_medico_sesion()
    if not id_doctor:
        return redirect(url_for("auth.login"))

    citas = obtener_citas_del_medico(id_doctor, "proximas")

    return render_template(
        "dashboard.html",
        citas=citas,
        nombre=session.get("nombre", "Doctor"),
        filtro="proximas"
    )


@medico.route("/agenda")
def agenda():
    if not acceso_medico():
        return redirect(url_for("auth.login"))

    id_doctor = obtener_id_medico_sesion()
    if not id_doctor:
        return redirect(url_for("auth.login"))

    filtro = request.args.get("filtro", default="proximas")
    citas = obtener_citas_del_medico(id_doctor, filtro)

    return render_template(
        "agenda.html",
        citas=citas,
        filtro=filtro,
        nombre=session.get("nombre", "Doctor")
    )


@medico.route("/panel_medico")
def panel_medico():
    """
    Ruta de compatibilidad por si todavía tienes links viejos.
    Ahora redirige al nuevo dashboard.
    """
    return redirect(url_for("medico.dashboard"))


@medico.route("/detalle_cita/<int:id_cita>", methods=["GET", "POST"])
def detalle_cita(id_cita):
    if not acceso_medico():
        return redirect(url_for("auth.login"))

    id_doctor = obtener_id_medico_sesion()
    if not id_doctor:
        return redirect(url_for("auth.login"))

    cita = obtener_detalle_cita(id_cita, id_doctor)

    if not cita:
        return redirect(url_for("medico.agenda"))

    if request.method == "POST":
        datos_generales = {
            "peso": request.form.get("peso"),
            "talla": request.form.get("talla"),
            "presion_arterial": request.form.get("presion_arterial"),
            "temperatura": request.form.get("temperatura"),
            "sangre": request.form.get("sangre"),
            "alergias": request.form.get("alergias"),
            "medicamentos_actuales": request.form.get("medicamentos_actuales"),
            "antecedentes": request.form.get("antecedentes"),
        }

        datos_consulta = {
            "diagnostico": request.form.get("diagnostico"),
            "tratamiento": request.form.get("tratamiento"),
            "observaciones": request.form.get("observaciones"),
        }

        datos_especialidad = {
            # Obstetricia
            "semanas_gestacion": request.form.get("semanas_gestacion"),
            "fum": request.form.get("fum"),
            "gestas": request.form.get("gestas"),
            "partos": request.form.get("partos"),
            "cesareas": request.form.get("cesareas"),
            "abortos": request.form.get("abortos"),
            "frecuencia_cardiaca_fetal": request.form.get("frecuencia_cardiaca_fetal"),
            "movimientos_fetales": request.form.get("movimientos_fetales"),
            "observaciones_obstetricia": request.form.get("observaciones_obstetricia"),

            # Dermatología
            "tipo_lesion": request.form.get("tipo_lesion"),
            "ubicacion_lesion": request.form.get("ubicacion_lesion"),
            "tiempo_evolucion": request.form.get("tiempo_evolucion"),
            "sintomas_asociados": request.form.get("sintomas_asociados"),
            "tratamiento_topico": request.form.get("tratamiento_topico"),
            "observaciones_dermatologia": request.form.get("observaciones_dermatologia"),

            # Nutrición
            "imc": request.form.get("imc"),
            "habitos_alimenticios": request.form.get("habitos_alimenticios"),
            "consumo_agua": request.form.get("consumo_agua"),
            "objetivo_nutricional": request.form.get("objetivo_nutricional"),
            "plan_alimenticio": request.form.get("plan_alimenticio"),
            "observaciones_nutricion": request.form.get("observaciones_nutricion"),

            # Psicología
            "motivo_psicologico": request.form.get("motivo_psicologico"),
            "estado_emocional": request.form.get("estado_emocional"),
            "evaluacion_mental": request.form.get("evaluacion_mental"),
            "plan_terapeutico": request.form.get("plan_terapeutico"),
            "observaciones_psicologia": request.form.get("observaciones_psicologia"),
        }

        guardar_consulta_completa(cita, datos_generales, datos_consulta, datos_especialidad)

        return redirect(
            url_for("medico.expediente_paciente", id_paciente=cita["id_paciente"])
        )

    return render_template("detalle_cita.html", cita=cita)


@medico.route("/expediente/<int:id_paciente>")
def expediente_paciente(id_paciente):
    if not acceso_medico():
        return redirect(url_for("auth.login"))

    paciente, historial = obtener_expediente_completo(id_paciente)

    return render_template(
        "expediente_paciente.html",
        paciente=paciente,
        historial=historial
    )