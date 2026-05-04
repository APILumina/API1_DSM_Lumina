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

# Query atualizada para buscar também a abreviação do partido
Lumina2 = '''
SELECT
    d.nome AS deputado,
    p.abreviacao AS partido,
    COUNT(*) AS presenca_nominal
FROM
    presencas pr
    JOIN deputado d ON pr.fk_deputado = d.cd_deputado
    JOIN partido p ON d.fk_partido = p.cd_partido
WHERE pr.presenca_nominal = 1
GROUP BY d.cd_deputado, d.nome, p.abreviacao
ORDER BY presenca_nominal DESC
LIMIT 20
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
    print(" Conexão bem-sucedida!")

    cursor = conn.cursor()
    cursor.execute(Lumina2)
    
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    
    print(f"Colunas: {columns}")
    print(f"Total de linhas: {len(data)}")
    
    df = pd.DataFrame(data, columns=columns)
    print(f" DataFrame criado com {len(df)} registros!")
    cursor.close()

    if len(df) == 0:
        print("Nenhum dado para gerar gráficos")
        exit()

    # Criamos uma nova coluna formatada: "Nome (PARTIDO)"
    df['exibicao'] = df['deputado'] + " (" + df['partido'] + ")"

    # Ordenação para o gráfico de barras horizontais (menor para maior para o Top 1 ficar no topo)
    df_top = df.sort_values('presenca_nominal', ascending=True)
    
    plt.figure(figsize=(12, 10))
    # Usamos a coluna 'exibicao' no eixo Y
    plt.barh(df_top['exibicao'], df_top['presenca_nominal'], color='steelblue')
    
    plt.title('Top 20 Deputados com Mais Presença - Brasil', fontsize=16, fontweight='bold')
    plt.xlabel('Total de Presenças', fontsize=12)
    plt.ylabel('Deputado (Partido)', fontsize=12)
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