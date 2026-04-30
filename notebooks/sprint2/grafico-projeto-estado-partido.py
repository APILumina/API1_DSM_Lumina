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

def gerar_grafico_projetos_aprovados(estado, partido):
    query = """
        SELECT d.nome_eleitoral, COUNT(pd.fk_proposicao) AS total
        FROM proposicao_deputados pd
        JOIN proposicoes p ON p.cd_proposicoes = pd.fk_proposicao
        JOIN deputado d    ON d.cd_deputado    = pd.fk_deputado
        JOIN partido pt    ON pt.cd_partido    = d.fk_partido
        JOIN estado e      ON e.cd_estado      = d.fk_estado
        WHERE p.status = 'Transformado em Norma Jurídica'
          AND pt.abreviacao = %s
          AND e.nome = %s
        GROUP BY d.cd_deputado, d.nome_eleitoral
        ORDER BY total DESC
    """

    try:
        conn = pymysql.connect(**config_mysql)
        df = pd.read_sql(query, conn, params=(partido, estado))
        conn.close()

        df_plot = df.sort_values("total", ascending=True) #maior para o menor

        fig, ax = plt.subplots(figsize=(10, max(2, len(df) * 0.5)))
        ax.barh(df_plot["nome_eleitoral"], df_plot["total"], color="#1A249D")
        ax.set_xlabel("Projetos Aprovados")
        ax.set_title(f"Projetos Aprovados — {partido} / {estado}")

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return

    if df.empty:
        print(f"Nenhum projeto aprovado encontrado para {partido} em {estado}.")
        return


# Exemplo de uso
gerar_grafico_projetos_aprovados("São Paulo", "PP")