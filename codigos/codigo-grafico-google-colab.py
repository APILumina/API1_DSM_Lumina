import pandas as pd
import matplotlib.pyplot as plt
from google.colab import drive as drive

drive.mount('/content/drive')

# -----------------------------#
# CRIANDO DATAFRAME
# -----------------------------#

df = pd.read_json('/content/drive/MyDrive/API1/dados_deputados.json') # Alterado de read_csv para read_json

#-----------------------------#
#Codigo para dar merge
#-----------------------------#

#df1 = pd.read_json('/content/drive/MyDrive/API1/dados_deputados.json')
#df2 = pd.read_json('/content/drive/MyDrive/API1/dados_deputados.json')

#df_final = pd.merge(df1, df2, on='deputado')

# -----------------------------#
# FUNÇÃO PARA GERAR GRÁFICOS
# -----------------------------#

def gerar_graficos_por_estado(df_estado, estado):

#-----------------------------#
# cria rótulos com nome + partido
#-----------------------------#

    labels = df_estado["deputado"] + " (" + df_estado["partido"] + ")"
    plt.figure(figsize=(20, 10))

    for criterio in ["gastos", "presenca", "projetos"]:
        plt.figure()
        plt.bar(labels, df_estado[criterio])

        plt.title(f"{criterio.capitalize()} - Comparação entre Deputados ({estado})")
        plt.xlabel("Deputados")
        plt.ylabel(criterio.capitalize())

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

# -----------------------------#
# GERAR GRÁFICOS POR ESTADO
# -----------------------------#

for estado in df["estado"].unique():
    df_estado = df[df["estado"] == estado]

    # só gera se tiver comparação
    if len(df_estado) > 1:
        gerar_graficos_por_estado(df_estado, estado)
