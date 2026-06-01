import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pymysql
import os

# Configurações de acesso
db_name = 'Lumina2'
db_user = 'root'
db_pass = 'lumina1234'
db_host = '54.198.148.230' 
db_port = 3306

# Query corrigida (COM tabela intermediária)
Lumina2 = '''
SELECT
    d.nome AS deputado,
    p.abreviacao AS partido,
    COUNT(*) AS total_aprovados
FROM
    proposicoes pr
    JOIN proposicao_deputados pd ON pr.cd_proposicoes = pd.fk_proposicao
    JOIN deputado d ON pd.fk_deputado = d.cd_deputado
    JOIN partido p ON d.fk_partido = p.cd_partido
WHERE 
    pr.status = 'Transformado em Norma Jurídica'
GROUP BY 
    d.cd_deputado, d.nome, p.abreviacao
ORDER BY 
    total_aprovados DESC
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
    print("Conexão bem-sucedida!")

    cursor = conn.cursor()
    cursor.execute(Lumina2)
    
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    
    print(f"Colunas: {columns}")
    print(f"Total de registros encontrados: {len(data)}")
    
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

    # Preparando dados
    df['exibicao'] = df['deputado'] + " (" + df['partido'] + ")"
    df_plot = df.sort_values('total_aprovados', ascending=True)

    # Criando gráfico
    plt.figure(figsize=(12, 10))
    plt.barh(df_plot['exibicao'], df_plot['total_aprovados'], color='steelblue')

    plt.title('Top 20 Deputados com Mais Projetos Aprovados', fontsize=16, fontweight='bold')
    plt.xlabel('Quantidade Total de Proposições (Normas Jurídicas)', fontsize=12)
    plt.ylabel('Deputado (Partido)', fontsize=12)
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
        print("Conexão fechada.")