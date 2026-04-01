from flask import Blueprint, render_template, request
from datos.consultas_panel import (
    obtener_doctores_panel,
    obtener_pacientes_panel_recepcion
)

panel = Blueprint("panel", __name__)

@panel.route("/panel_citas")
def panel_citas():
    q = request.args.get("q", "").strip()

    doctores = obtener_doctores_panel()
    pacientes_panel = obtener_pacientes_panel_recepcion(q)

    resumen_panel = {
        "prospectos": sum(1 for p in pacientes_panel if p["total_citas"] == 1),
        "recurrentes": sum(1 for p in pacientes_panel if p["total_citas"] >= 2),
        "activas": sum(1 for p in pacientes_panel if p["estado_cuenta"] == "Cuenta activa")
    }

    return render_template(
        "panel_citas.html",
        doctores=doctores,
        pacientes_panel=pacientes_panel,
        resumen_panel=resumen_panel
    )