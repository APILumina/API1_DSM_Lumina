import io #Pra fazer os gráficos serem temporários
import base64 #Para converter as img em "Strings"
from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

@app.route("/")
def graph_rank_gasto():
    df1 = pd.read_csv(
        "data/deputados/tratado/ranking_gastos_deputados.csv",
        sep=";",
        encoding="utf-8"
    )

    ranking = df1.groupby('nome')['valor'].sum().sort_values().tail(20)

    plt.figure(figsize=(10, 10))
    ranking.plot(kind='barh', color='#1f77b4')
    plt.title('Ranking de Gastos Deputados')
    plt.tight_layout()

    img1 = io.BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    grafico_gastos = base64.b64encode(img1.getvalue()).decode()
    plt.close()

    df2 = pd.read_csv(
        "data/deputados/tratado/ranking_presencas_deputados.csv",
        sep=";",
        encoding="utf-8"
    )

    ranking2 = df2.groupby('nome')['total_presencas'].sum().sort_values().tail(20)

    plt.figure(figsize=(10, 10))
    ranking2.plot(kind='barh', color='#1f77b4')
    plt.title('Ranking de Presenças Deputados')
    plt.tight_layout()

    img2 = io.BytesIO()
    plt.savefig(img2, format='png')
    img2.seek(0)
    grafico_presencas = base64.b64encode(img2.getvalue()).decode()
    plt.close()

    return render_template(
        "home.html",
        grafico_gastos=grafico_gastos,
        grafico_presencas=grafico_presencas
    )