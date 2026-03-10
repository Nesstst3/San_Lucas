from flask import Blueprint, render_template, request
from datos.consultas_panel import obtener_doctores_panel, obtener_citas_por_doctor_y_filtro

panel = Blueprint("panel", __name__)

@panel.route("/panel_citas", methods=["GET"])
def panel_citas():
    doctores = obtener_doctores_panel()

    id_doctor = request.args.get("id_doctor", type=int)
    filtro = request.args.get("filtro", default="proximas")

    citas = []
    doctor_seleccionado = None

    if id_doctor:
        citas = obtener_citas_por_doctor_y_filtro(id_doctor, filtro)
        doctor_seleccionado = next(
            (d for d in doctores if d["id_doctor"] == id_doctor),
            None
        )

    return render_template(
        "panel_citas.html",
        doctores=doctores,
        citas=citas,
        filtro=filtro,
        id_doctor=id_doctor,
        doctor_seleccionado=doctor_seleccionado
    )