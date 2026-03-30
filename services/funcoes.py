import io
import base64
import pandas as pd
import matplotlib.pyplot as plt

def gerar_graficos():

    # Gastos

    df1 = pd.read_csv("data/deputados/tratado/ranking_gastos_deputados.csv", sep=";", encoding="utf-8")
    ranking = df1.groupby('nome')['valor'].sum().sort_values().tail(10)

    plt.figure(figsize=(6, 6))
    ranking.plot(kind='bar')
    
    plt.title('Total de Gastos por Deputado')
    plt.ylabel('Soma de Gastos')
    plt.xlabel('Deputado')

    plt.tight_layout()

    img1 = io.BytesIO()
    plt.savefig(img1, format='png')
    img1.seek(0)
    grafico_gastos = base64.b64encode(img1.getvalue()).decode()
    plt.close()

    # Presenças

    df2 = pd.read_csv("data/deputados/tratado/ranking_presencas_deputados.csv", sep=";", encoding="utf-8")
    ranking2 = df2.groupby('nome')['total_presencas'].sum().sort_values().tail(10)

    plt.figure(figsize=(6, 6))
    ranking2.plot(kind='bar')
    
    plt.title('Total de presença por deputado')
    plt.ylabel('Soma de Presenças')
    plt.xlabel('Deputado')

    plt.tight_layout()

    img3 = io.BytesIO()
    plt.savefig(img3, format='png')
    img3.seek(0)
    grafico_presencas = base64.b64encode(img3.getvalue()).decode()
    plt.close()

    # Presença estado

    df3 = pd.read_csv("data/deputados/tratado/ranking_presencas_deputados.csv", sep=";", encoding="utf-8")
    ranking_uf = df3.groupby('uf')['total_presencas'].sum().sort_values()

    plt.figure(figsize=(10, 8)) 
    ranking_uf.plot(kind='bar')

    plt.title('Total de Presença por Estado')
    plt.ylabel('Soma de Presenças')
    plt.xlabel('Estado (UF)')

    img_uf = io.BytesIO()
    plt.savefig(img_uf, format='png')
    img_uf.seek(0)
    grafico_presencas_uf = base64.b64encode(img_uf.getvalue()).decode()
    plt.close()

    #Gasto estado

    df4 = pd.read_csv("data/deputados/tratado/ranking_gastos_deputados.csv", sep=";", encoding="utf-8")
    ranking_uf2 = df4.groupby('uf')['valor'].sum().sort_values()

    plt.figure(figsize=(10, 8)) 
    ranking_uf2.plot(kind='bar')

    plt.title('Total de gasto por Estado')
    plt.ylabel('Soma de gastos')
    plt.xlabel('Estado (UF)')

    img_uf2 = io.BytesIO()
    img_uf2.seek(0)
    grafico_presencas_uf2 = base64.b64encode(img_uf2.getvalue()).decode()
    plt.close()

    # Projeto aprovados estado

    df5 = pd.read_csv("data/deputados/tratado/ranking_gastos_deputados.csv", sep=";", encoding="utf-8")
    ranking_uf3 = df5.groupby('uf')['valor'].sum().sort_values()

    plt.figure(figsize=(10, 8)) 
    ranking_uf3.plot(kind='bar')

    plt.title('Total de gasto por Estado')
    plt.ylabel('Soma de gastos')
    plt.xlabel('Estado (UF)')

    img_uf3 = io.BytesIO()
    plt.savefig(img_uf3, format='png')
    img_uf3.seek(0)
    grafico_presencas_uf2 = base64.b64encode(img_uf3.getvalue()).decode()
    plt.close()

    return grafico_gastos, grafico_presencas,grafico_presencas_uf,grafico_presencas_uf2

