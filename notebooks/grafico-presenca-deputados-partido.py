import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pymysql
import os

db_name = 'Lumina2'
db_user = 'root'
db_pass = 'lumina1234'
db_host = '3.89.28.59' 
db_port = 3306

# Query que rankeia os deputados dentro de cada partido
Lumina2 = '''
SELECT * FROM (
    SELECT
        d.nome AS deputado,
        p.abreviacao AS partido,
        COUNT(*) AS presenca_nominal,
        ROW_NUMBER() OVER (PARTITION BY p.abreviacao ORDER BY COUNT(*) DESC) as ranking
    FROM
        presencas pr
        JOIN deputado d ON pr.fk_deputado = d.cd_deputado
        JOIN partido p ON d.fk_partido = p.cd_partido
    WHERE pr.presenca_nominal = 1
    GROUP BY d.cd_deputado, d.nome, p.abreviacao
) AS ranked_stats
WHERE ranking <= 20
'''

df = None
try:
    conn = pymysql.connect(
        database=db_name,
        user=db_user,
        password=db_pass,
        host=db_host,
        port=db_port,
    )
    print("Conexão bem-sucedida!")

    cursor = conn.cursor()
    cursor.execute(Lumina2)
    
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    
    df = pd.DataFrame(data, columns=columns)
    print(f"DataFrame criado com {len(df)} registros totais!")
    cursor.close()

    if len(df) == 0:
        print("Nenhum dado para gerar gráficos")
        exit()

    # Um gráfico por PARTIDO (mostrando os 20 melhores de cada)
    for partido in df['partido'].unique():
        # Filtra o partido e ordena do menor para o maior para o barh
        df_partido = df[df['partido'] == partido].sort_values('presenca_nominal', ascending=True)
        
        plt.figure(figsize=(10, 8))
        plt.barh(df_partido['deputado'], df_partido['presenca_nominal'], color='steelblue')
        
        plt.title(f'Top 20 Presenças - Partido {partido}', fontsize=16, fontweight='bold')
        plt.xlabel('Total de Presenças', fontsize=12)
        plt.ylabel('Deputado', fontsize=12)
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()

        plt.show()
        plt.close()

except pymysql.Error as err:
    print(f"Erro de banco de dados: {err}")
except Exception as err:
    print(f"Erro: {err}")
finally:
    if 'conn' in locals():
        conn.close()
        print(" Conexão fechada.")