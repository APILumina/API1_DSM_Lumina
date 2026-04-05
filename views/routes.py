from flask import Blueprint, render_template

route_bp =Blueprint("route",__name__)

@route_bp.route("/")
def home():
    return render_template ("home.html")

@route_bp.route("/graficos")
def graficos():
    return render_template("graficos.html")

@route_bp.route("/deputados")
def deputados():
    return render_template("deputados.html")

@route_bp.route("/infodeputados")
def infodeputados():
    return render_template("infodeputados.html")