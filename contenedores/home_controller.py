from flask import Blueprint, render_template
from datos.consultas_generales import obtener_especialidades, obtener_doctores

home = Blueprint("home", __name__)

@home.route("/")
def inicio():
    especialidades = obtener_especialidades()
    doctores = obtener_doctores()

    return render_template(
        "index.html",
        especialidades=especialidades,
        doctores=doctores
    )