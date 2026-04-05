from flask import Blueprint, render_template

route_bp =Blueprint("route",__name__)

@route_bp.route("/")
def home():
    return render_template ("index.html")

@route_bp.route("/graficos")
def graficos():
    return render_template("graficos.html")

@route_bp.route("/deputados")
def deputados():
    return render_template("deputados.html")

@route_bp.route("/deputado")
def infodeputados():
    return render_template("deputado.html")

@route_bp.route("/estado")
def estado():
    return render_template("deputados-estados.html")

@route_bp.route("/partido")
def partido():
    return render_template("escolha-partido.html")
