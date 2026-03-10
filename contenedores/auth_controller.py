from flask import Blueprint, render_template, request, redirect, url_for, session
from datos.consultas_auth import autenticar_usuario

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    mensaje = None

    if request.method == "POST":
        correo = request.form.get("correo")
        contrasena = request.form.get("contrasena")

        usuario = autenticar_usuario(correo, contrasena)

        if usuario:
            session["id_usuario"] = usuario["id_usuario"]
            session["correo"] = usuario["correo"]
            session["rol"] = usuario["rol"]
            session["id_doctor"] = usuario["id_doctor"]

            if usuario["rol"] == "recepcion":
                return redirect(url_for("panel.panel_citas"))

            if usuario["rol"] == "medico":
                return redirect(url_for("medico.panel_medico"))

        mensaje = "Correo o contraseña incorrectos."

    return render_template("login.html", mensaje=mensaje)


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))