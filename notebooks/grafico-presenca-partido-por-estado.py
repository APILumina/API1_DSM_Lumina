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

Lumina2 = '''
SELECT
    e.nome AS estado,
    p.abreviacao,
    COUNT(*) AS presenca_nominal
FROM
    presencas pr
    JOIN deputado d ON pr.fk_deputado = d.cd_deputado
    JOIN partido p ON d.fk_partido = p.cd_partido
    JOIN estado e ON d.fk_estado = e.cd_estado
WHERE pr.presenca_nominal = 1
GROUP BY e.nome, p.abreviacao
ORDER BY e.nome, presenca_nominal DESC
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
    
    print(f"Colunas: {columns}")
    print(f"Total de linhas: {len(data)}")
    if data:
        print(f"Primeiras 3 linhas: {data[:3]}")
    else:
        print("ATENÇÃO: Nenhum dado retornado!")
    
    df = pd.DataFrame(data, columns=columns)
    print(f"DataFrame criado com {len(df)} registros!")
    cursor.close()

    if len(df) == 0:
        print("Nenhum dado para gerar gráficos")
        exit()


    # Um gráfico por estado
    for estado in df['estado'].unique():
        df_estado = df[df['estado'] == estado].sort_values('presenca_nominal', ascending=True)
        
        plt.figure(figsize=(10, 8))
        plt.barh(df_estado['abreviacao'], df_estado['presenca_nominal'], color='steelblue')
        plt.title(f'Presença dos Partidos - {estado}', fontsize=16, fontweight='bold')
        plt.xlabel('Total de Presenças', fontsize=12)
        plt.ylabel('Partido', fontsize=12)
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()

        plt.show()
        plt.close()

except pymysql.Error as err:
    print(f"Erro de banco de dados: {err}")
    import traceback
    traceback.print_exc()
except Exception as err:
    print(f"Erro: {err}")
    import traceback
    traceback.print_exc()
finally:
    if 'conn' in locals():
        conn.close()
        print(" Conexão fechada.")