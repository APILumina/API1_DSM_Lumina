import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pymysql

# Configurações do banco
config_mysql = {
    "host": "54.198.148.230",
    "user": "root",
    "password": "lumina1234",
    "database": "Lumina2",
    "port": 3306,
}

def gerar_grafico_gastos(estado, partido_abreviacao):
    conn = None
    try:
        conn = pymysql.connect(**config_mysql)

        query = f"""
        SELECT
            d.nome_eleitoral,
            p.abreviacao,
            SUM(v.gasto_total) AS total_gasto
        FROM v_despesas_completas v
        INNER JOIN partido p ON v.cd_partido = p.cd_partido
        INNER JOIN deputado d ON v.nome_deputado = d.nome
        WHERE v.nome_estado = '{estado}'
          AND p.abreviacao = '{partido_abreviacao}'
        GROUP BY d.nome_eleitoral, p.abreviacao
        ORDER BY total_gasto DESC
        """

        df = pd.read_sql(query, conn)

        if df.empty:
            print(f"Nenhum dado encontrado para {partido_abreviacao} em {estado}.")
            return

        abreviacao = df['abreviacao'].iloc[0]
        df = df.sort_values('total_gasto', ascending=True)

        #Visual
        n = len(df)
        fig, ax = plt.subplots(figsize=(12, max(4, n * 0.4)))

        ax.barh(df['nome_eleitoral'], df['total_gasto'], color='#1A249D', height=0.6)

        #Valor no final das barras
        for i, valor in enumerate(df['total_gasto']):
            ax.text(
                valor + df['total_gasto'].max() * 0.01,
                i,
                f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                va='center', fontsize=8, color='#444444'
            )

        #Configurações do eixo X
        ax.xaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"R$ {x/1_000:.0f}k")
        )
        ax.set_xlim(0, df['total_gasto'].max() * 1.2) #limite para o eixo x
        ax.set_title(f'Gastos dos Deputados — {abreviacao} ({estado})', fontsize=13, fontweight='bold')
        ax.set_xlabel('Gasto Total (R$)')

        
        ax.grid(axis='x', linestyle='--', alpha=0.3)

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Erro: {e}")
      
    finally:
        if conn:
            conn.close()

#Exemplo
gerar_grafico_gastos('Bahia', 'PT')