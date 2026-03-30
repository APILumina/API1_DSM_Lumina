from flask import Blueprint, render_template
from services.funcoes import gerar_graficos

graficos_bp = Blueprint("graficos", __name__)

@graficos_bp.route("/")
def home():
    grafico_gastos, grafico_presencas,grafico_presencas_uf,grafico_presencas_uf2 = gerar_graficos()

    return render_template(
        "home.html",
        grafico_gastos=grafico_gastos,
        grafico_presencas=grafico_presencas,
        grafico_presencas_uf =grafico_presencas_uf,
        grafico_presencas_uf2=grafico_presencas_uf2
    )