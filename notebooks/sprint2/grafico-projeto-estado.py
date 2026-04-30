import pandas as pd
import matplotlib.pyplot as plt
import pymysql

config_mysql = {
    "host": "54.198.148.230",
    "user": "root",
    "password": "lumina1234",
    "database": "Lumina2",
    "port": 3306,
}

def gerar_ranking_propostos(estado_selecionado):

    conn = None
    try:
        #Conecta ao banco
        conn = pymysql.connect(**config_mysql)

        query = """
            SELECT p.abreviacao AS partido,
            COUNT(DISTINCT pd.fk_proposicao) AS total_aprovados
            FROM proposicao_deputados pd
            JOIN proposicoes pr
                ON pd.fk_proposicao = pr.cd_proposicoes
            JOIN deputado d
                ON pd.fk_deputado = d.cd_deputado
            JOIN partido p
                ON d.fk_partido = p.cd_partido
            JOIN estado e
                ON d.fk_estado = e.cd_estado
            WHERE pr.status = 'Transformado em Norma Jurídica'
            AND e.nome = %s GROUP BY p.abreviacao
            ORDER BY total_aprovados DESC
        """

        df = pd.read_sql(query, conn, params=(estado_selecionado,))

        if df.empty:
            print(f"Nenhuma proposição aprovada encontrada para o estado: {estado_selecionado}")
            return

        #Gráfico
        df_plot = df.sort_values("total_aprovados", ascending=True)  #menor → maior (o barh inverte)

        fig, ax = plt.subplots(figsize=(8, max(2, len(df_plot) * 0.5)))

        bars = ax.barh(df_plot["partido"], df_plot["total_aprovados"], color='#1A249D')

        #Valor ao lado da barra
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + 0.1,
                bar.get_y() + bar.get_height() / 2, #centraliza
                str(int(width)),
                ha="left",
                va="center",
                fontsize=9,
            )

        ax.set_title(f"Proposições aprovadas dos partidos - {estado_selecionado}", fontsize=13, fontweight="bold", pad=10)
        ax.set_xlabel("Total de proposições aprovadas", fontsize=10)
        ax.set_xlim(0, df_plot["total_aprovados"].max() * 1.1)
        ax.grid(axis="x", linestyle="--", alpha=0.4)

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Erro: {e}")

    finally:
        if conn:
            conn.close()


#Exemplo
gerar_ranking_propostos("São Paulo")