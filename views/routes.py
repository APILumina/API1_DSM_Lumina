from flask import Blueprint, render_template, request, jsonify, url_for
import mysql
from database import conectar
import unicodedata
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io, base64
import pandas as pd
from datetime import datetime

route_bp = Blueprint("route", __name__)

partidos = [
    {'abreviacao': 'AVANTE', 'nome': 'Avante'},
    {'abreviacao': 'CIDADANIA', 'nome': 'Cidadania'}, #FALTA IMAGEM
    {'abreviacao': 'MDB', 'nome': 'Movimento Democrático Brasileiro'},
    {'abreviacao': 'MISSÃO', 'nome': 'Partido Missão'},
    {'abreviacao': 'NOVO', 'nome': 'Partido Novo'},
    {'abreviacao': 'PCdoB', 'nome': 'Partido Comunista do Brasil'},
    {'abreviacao': 'PDT', 'nome': 'Partido Democrático Trabalhista'},
    {'abreviacao': 'PL', 'nome': 'Partido Liberal'},
    {'abreviacao': 'PODE', 'nome': 'Podemos'},
    {'abreviacao': 'PP', 'nome': 'Progressistas'},
    {'abreviacao': 'PRD', 'nome': 'Partido da Mobilização Nacional'},
    {'abreviacao': 'PSB', 'nome': 'Partido Socialista Brasileiro'},
    {'abreviacao': 'PSD', 'nome': 'Partido Social Democrático'},
    {'abreviacao': 'PSDB', 'nome': 'Partido da Social Democracia Brasileira'},
    {'abreviacao': 'PSOL', 'nome': 'Partido Socialismo e Liberdade'},
    {'abreviacao': 'PT', 'nome': 'Partido dos Trabalhadores'},
    {'abreviacao': 'PV', 'nome': 'Partido Verde'},
    {'abreviacao': 'REDE', 'nome': 'Rede Sustentabilidade'},
    {'abreviacao': 'REPUBLICANOS', 'nome': 'Republicanos'},
    {'abreviacao': 'SOLIDARIEDADE', 'nome': 'Solidariedade'},
    {'abreviacao': 'UNIÃO', 'nome': 'União Brasil'}
]

estados = [
    {'uf': 'AC', 'nome': 'Acre'},
    {'uf': 'AL', 'nome': 'Alagoas'},
    {'uf': 'AP', 'nome': 'Amapá'},
    {'uf': 'AM', 'nome': 'Amazonas'},
    {'uf': 'BA', 'nome': 'Bahia'},
    {'uf': 'CE', 'nome': 'Ceará'},
    {'uf': 'DF', 'nome': 'Distrito Federal'},
    {'uf': 'ES', 'nome': 'Espírito Santo'},
    {'uf': 'GO', 'nome': 'Goiás'},
    {'uf': 'MA', 'nome': 'Maranhão'},
    {'uf': 'MT', 'nome': 'Mato Grosso'},
    {'uf': 'MS', 'nome': 'Mato Grosso do Sul'},
    {'uf': 'MG', 'nome': 'Minas Gerais'},
    {'uf': 'PA', 'nome': 'Pará'},
    {'uf': 'PB', 'nome': 'Paraíba'},
    {'uf': 'PR', 'nome': 'Paraná'},
    {'uf': 'PE', 'nome': 'Pernambuco'},
    {'uf': 'PI', 'nome': 'Piauí'},
    {'uf': 'RJ', 'nome': 'Rio de Janeiro'},
    {'uf': 'RN', 'nome': 'Rio Grande do Norte'},
    {'uf': 'RS', 'nome': 'Rio Grande do Sul'},
    {'uf': 'RO', 'nome': 'Rondônia'},
    {'uf': 'RR', 'nome': 'Roraima'},
    {'uf': 'SC', 'nome': 'Santa Catarina'},
    {'uf': 'SP', 'nome': 'São Paulo'},
    {'uf': 'SE', 'nome': 'Sergipe'},
    {'uf': 'TO', 'nome': 'Tocantins'}
]

def obter_partidos_abreviados():
    return sorted([p['abreviacao'] for p in partidos])


def gerar_grafico_deputado(valor_deputado, valor_media, titulo):
    # Ajustado para o mesmo tamanho do gráfico de temas
    fig, ax = plt.subplots(figsize=(6, 6)) 
    
    cores = ['#1A249D', "#efc33c"]
    labels = ['Este Deputado', 'Média da Câmara']
    valores = [valor_deputado, valor_media]
    
    barras = ax.bar(labels, valores, color=cores, width=0.5)
    ax.set_title(titulo, pad=15, fontsize=12, fontweight='bold', color='#081638')
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#cccccc')
    
    for barra in barras:
        altura = barra.get_height()
        ax.text(barra.get_x() + barra.get_width()/2., altura + (altura * 0.02),
                f'{altura:.1f}', ha='center', va='bottom', fontweight='bold', color='#081638')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=100)
    plt.close(fig)
    buf.seek(0)
    
    return base64.b64encode(buf.getvalue()).decode('utf-8')
# Função auxiliar para gerar gráfico em memória
def gerar_grafico(df, col_x, col_y, titulo):
    if df.empty:
        return None
    
    df = df.sort_values(by=col_y, ascending=True)  # <- aqui
    
    cores = ["#1C1A9D","#3c66ef"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(df[col_x], df[col_y], color=cores)
    ax.set_title(titulo, fontweight='bold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True)
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def gerar_grafico_temas(labels, valores_deputado, valores_media, titulo):
    """Gera gráfico de barras horizontais comparando deputado vs média da câmara por tema."""
    if not labels:
        return None
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    y = range(len(labels))
    height = 0.35
    y_dep = [pos - height/2 for pos in y]
    y_med = [pos + height/2 for pos in y]
    
    ax.barh(y_dep, valores_deputado, height, label='Este Deputado', color='#1A249D')
    ax.barh(y_med, valores_media, height, label='Média da Câmara', color='#efc33c')
    
    ax.set_title(titulo, pad=15, fontsize=12, fontweight='bold', color='#081638')
    ax.set_yticks(list(y))
    ax.set_yticklabels(labels, fontsize=10)
    ax.legend()
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', transparent=True, dpi=100)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@route_bp.route("/")
def home():
    conn   = conectar()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
    SELECT nome,imagem_deputado
    FROM deputado
    ORDER BY nome
    """)

    todos_deputados = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template("index.html", partidos=partidos, estados=estados, hide_pesquisa=True, sticky_navbar=True,todos_deputados=todos_deputados, nb=1)


@route_bp.route("/graficos")
def graficos():
    estado  = request.args.get('estado', '')
    partido = request.args.get('partido', '')

    conn   = conectar()
    cursor = conn.cursor(dictionary=True)

    grafico_projetos = None
    grafico_presenca = None
    grafico_gastos   = None

    # ─────────────────────────────────────────
    # CENÁRIO 1: só estado → agrupa por partido
    # ─────────────────────────────────────────
    if estado and not partido:

        cursor.execute("""
            SELECT p.abreviacao AS label, COUNT(*) AS total
            FROM proposicao_deputados pd
            JOIN deputado d ON pd.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido   = p.cd_partido
            JOIN estado e   ON d.fk_estado    = e.cd_estado
            WHERE e.uf = %s
            GROUP BY p.abreviacao ORDER BY total DESC
        """, (estado,))
        grafico_projetos = gerar_grafico(pd.DataFrame(cursor.fetchall()), 'label', 'total', f'Projetos por Partido — {estado}')

        cursor.execute("""
            SELECT p.abreviacao AS label, AVG(t.taxa_assiduidade) AS total
            FROM taxa_presenca t
            JOIN deputado d ON t.fk_deputado  = d.cd_deputado
            JOIN partido p  ON d.fk_partido   = p.cd_partido
            JOIN estado e   ON d.fk_estado    = e.cd_estado
            WHERE e.uf = %s
            GROUP BY p.abreviacao ORDER BY total DESC
        """, (estado,))
        grafico_presenca = gerar_grafico(pd.DataFrame(cursor.fetchall()), 'label', 'total', f'Presença Média por Partido — {estado}')

        cursor.execute("""
            SELECT p.abreviacao AS label,
                   SUM(CAST(REPLACE(g.gasto_total, ',', '.') AS DECIMAL(10,2))) AS total
            FROM despesas g
            JOIN deputado d ON g.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido  = p.cd_partido
            JOIN estado e   ON d.fk_estado   = e.cd_estado
            WHERE e.uf = %s
            GROUP BY p.abreviacao ORDER BY total DESC
        """, (estado,))
        grafico_gastos = gerar_grafico(pd.DataFrame(cursor.fetchall()), 'label', 'total', f'Gastos por Partido — {estado}')

    # ─────────────────────────────────────────
    # CENÁRIO 2: só partido → agrupa por estado
    # ─────────────────────────────────────────
    elif partido and not estado:

        cursor.execute("""
            SELECT e.uf AS label, COUNT(*) AS total
            FROM proposicao_deputados pd
            JOIN proposicoes pr ON pd.fk_proposicao = pr.cd_proposicoes
            JOIN deputado d ON pd.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido   = p.cd_partido
            JOIN estado e   ON d.fk_estado    = e.cd_estado
            WHERE p.abreviacao = %s AND pr.status = 'Transformado em Norma Jurídica'
            GROUP BY e.uf ORDER BY total DESC
        """, (partido,))
        grafico_projetos = gerar_grafico(pd.DataFrame(cursor.fetchall()), 'label', 'total', f'Projetos por Estado — {partido}')

        cursor.execute("""
            SELECT e.uf AS label, AVG(t.taxa_assiduidade) AS total
            FROM taxa_presenca t
            JOIN deputado d ON t.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido  = p.cd_partido
            JOIN estado e   ON d.fk_estado   = e.cd_estado
            WHERE p.abreviacao = %s
            GROUP BY e.uf ORDER BY total DESC
        """, (partido,))
        grafico_presenca = gerar_grafico(pd.DataFrame(cursor.fetchall()), 'label', 'total', f'Presença Média por Estado — {partido}')

        cursor.execute("""
            SELECT e.uf AS label,
                   SUM(CAST(REPLACE(g.gasto_total, ',', '.') AS DECIMAL(10,2))) AS total
            FROM despesas g
            JOIN deputado d ON g.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido  = p.cd_partido
            JOIN estado e   ON d.fk_estado   = e.cd_estado
            WHERE p.abreviacao = %s
            GROUP BY e.uf ORDER BY total DESC
        """, (partido,))
        grafico_gastos = gerar_grafico(pd.DataFrame(cursor.fetchall()), 'label', 'total', f'Gastos por Estado — {partido}')

    # ─────────────────────────────────────────
    # CENÁRIO 3: estado + partido → top deputados
    # ─────────────────────────────────────────
    elif estado and partido:

        cursor.execute("""
            SELECT d.nome_eleitoral AS label, COUNT(*) AS total
            FROM proposicao_deputados pd
            JOIN proposicoes pr ON pd.fk_proposicao = pr.cd_proposicoes
            JOIN deputado d ON pd.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido   = p.cd_partido
            JOIN estado e   ON d.fk_estado    = e.cd_estado
            WHERE e.uf = %s AND p.abreviacao = %s AND pr.status = 'Transformado em Norma Jurídica'
            GROUP BY d.cd_deputado, d.nome_eleitoral ORDER BY total DESC
            LIMIT 20
        """, (estado, partido))
        grafico_projetos = gerar_grafico(pd.DataFrame(cursor.fetchall()), 'label', 'total', f'Projetos por Deputado — {partido} / {estado}')

        cursor.execute("""
            SELECT d.nome_eleitoral AS label, t.taxa_assiduidade AS total
            FROM taxa_presenca t
            JOIN deputado d ON t.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido  = p.cd_partido
            JOIN estado e   ON d.fk_estado   = e.cd_estado
            WHERE e.uf = %s AND p.abreviacao = %s
            ORDER BY total DESC
            LIMIT 20
        """, (estado, partido))
        grafico_presenca = gerar_grafico(pd.DataFrame(cursor.fetchall()), 'label', 'total', f'Presença por Deputado — {partido} / {estado}')

        cursor.execute("""
            SELECT d.nome_eleitoral AS label,
                   SUM(CAST(REPLACE(g.gasto_total, ',', '.') AS DECIMAL(10,2))) AS total
            FROM despesas g
            JOIN deputado d ON g.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido  = p.cd_partido
            JOIN estado e   ON d.fk_estado   = e.cd_estado
            WHERE e.uf = %s AND p.abreviacao = %s
            GROUP BY d.cd_deputado, d.nome_eleitoral ORDER BY total DESC
            LIMIT 20
        """, (estado, partido))
        grafico_gastos = gerar_grafico(pd.DataFrame(cursor.fetchall()), 'label', 'total', f'Gastos por Deputado — {partido} / {estado}')

    # ─────────────────────────────────────────
    # CENÁRIO 0: nenhum filtro → visão geral
    # ─────────────────────────────────────────
    else:

        cursor.execute("""
            SELECT e.uf AS label, COUNT(*) AS total
            FROM proposicao_deputados pd
            JOIN proposicoes pr ON pd.fk_proposicao = pr.cd_proposicoes
            JOIN deputado d ON pd.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido   = p.cd_partido
            JOIN estado e   ON d.fk_estado    = e.cd_estado
            WHERE pr.status = 'Transformado em Norma Jurídica'
            GROUP BY e.uf 
            ORDER BY total DESC
        """)
        grafico_projetos = gerar_grafico(pd.DataFrame(cursor.fetchall()), 'label', 'total', 'Projetos por Partido — Brasil')

        cursor.execute("""
            SELECT p.abreviacao AS label, AVG(t.taxa_assiduidade) AS total
            FROM taxa_presenca t
            JOIN deputado d ON t.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido  = p.cd_partido
            GROUP BY p.abreviacao ORDER BY total DESC
        """)
        grafico_presenca = gerar_grafico(pd.DataFrame(cursor.fetchall()), 'label', 'total', 'Presença Média por Partido — Brasil')

        cursor.execute("""
            SELECT p.abreviacao AS label,
                   SUM(CAST(REPLACE(g.gasto_total, ',', '.') AS DECIMAL(10,2))) AS total
            FROM despesas g
            JOIN deputado d ON g.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido  = p.cd_partido
            GROUP BY p.abreviacao ORDER BY total DESC
        """)
        grafico_gastos = gerar_grafico(pd.DataFrame(cursor.fetchall()), 'label', 'total', 'Gastos por Partido — Brasil')

    cursor.execute("""
    SELECT nome,imagem_deputado
    FROM deputado
    ORDER BY nome
    """)

    todos_deputados = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("graficos.html",
        estado=estado,
        estados=estados,
        partido=partido,
        partidos=partidos,
        grafico_projetos=grafico_projetos,
        grafico_presenca=grafico_presenca,
        grafico_gastos=grafico_gastos,
        todos_deputados=todos_deputados,
        nb=3
    )


@route_bp.route("/deputados")
def deputados():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    estado  = request.args.get('estado', '')
    partido = request.args.get('partido', '')
    tema    = request.args.get('tema', '')

    filtros = []
    params  = []
    
    joins = ""

    if estado:
        filtros.append("e.uf = %s")
        params.append(estado)   

    if partido:
        filtros.append("p.abreviacao = %s")
        params.append(partido)
        
    if tema:
        joins += """
        JOIN deputado_tema dt
            ON dt.fk_deputado = d.cd_deputado

        JOIN top_temas t
            ON t.cd_tp_temas = dt.fk_tema
        """
        
        filtros.append("t.cd_tp_temas = %s")
        params.append(tema)

    where = ("WHERE " + " AND ".join(filtros)) if filtros else ""


    query = f"""
    SELECT 
        d.cd_deputado,
        d.nome,
        d.nome_eleitoral,
        d.imagem_deputado,
        e.uf AS estado,
        p.abreviacao AS partido
    FROM deputado d
    JOIN estado e ON d.fk_estado = e.cd_estado
    JOIN partido p ON d.fk_partido = p.cd_partido
    {joins}
    {where}
    ORDER BY d.nome_eleitoral
    LIMIT 24 OFFSET 0
    """

    cursor.execute(query, params)
    dados = cursor.fetchall()

    cursor.execute("""
    SELECT nome, imagem_deputado
    FROM deputado
    ORDER BY nome
    """)

    todos_deputados = cursor.fetchall()

    cursor.execute("""
        SELECT tipo, cd_tp_temas
        FROM top_temas
    """)

    temas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "deputados.html",
        deputados=dados,
        estados=estados,
        estado=estado,
        partido=partido,
        tema=tema,
        partidos=partidos,
        todos_deputados=todos_deputados,
        temas=temas,
        sticky_navbar=True,
        nb=2
    )

@route_bp.route("/dados/deputados")
def dados_deputados():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    page   = int(request.args.get('page', 1))
    estado = request.args.get('estado', '')
    partido = request.args.get('partido', '')

    itens_por_pagina = 24
    offset = (page - 1) * itens_por_pagina

    filtros = []
    params  = []

    if estado and estado != 'Estado':
        filtros.append("e.uf = %s")
        params.append(estado)
    if partido and partido != 'Partido':
        filtros.append("p.abreviacao = %s")
        params.append(partido)

    where = ("WHERE " + " AND ".join(filtros)) if filtros else ""

    query = f"""
    SELECT d.cd_deputado, d.nome, d.nome_eleitoral, d.imagem_deputado,
           e.uf AS estado, p.abreviacao AS partido
    FROM deputado d
    JOIN estado e ON d.fk_estado = e.cd_estado
    JOIN partido p ON d.fk_partido = p.cd_partido
    {where}
    ORDER BY d.nome_eleitoral
    LIMIT %s OFFSET %s
    """

    params.extend([itens_por_pagina, offset])
    cursor.execute(query, params)
    dados = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(dados)

@route_bp.route("/deputado/<int:id>")
def infodeputados(id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    # ═══════════════════════════════════════════════════════════
    # DEFINIÇÃO DE QUERIES
    # ═══════════════════════════════════════════════════════════
    
    # Query 1: Dados básicos do deputado
    query1 = """
        SELECT 
            d.cd_deputado, d.nome, d.nome_eleitoral, d.email, d.imagem_deputado,
            e.uf AS estado, p.abreviacao AS partido
        FROM deputado d
        JOIN estado e ON fk_estado = e.cd_estado
        JOIN partido p ON fk_partido = p.cd_partido
        WHERE d.cd_deputado = %s
    """
    
    # Query 2: Total de gastos
    query2 = """
        SELECT COALESCE(SUM(CAST(REPLACE(g.gasto_total, ',', '.') AS DECIMAL(10,2))), 0) AS total
        FROM despesas g
        WHERE g.fk_deputado = %s
    """
    
    # Query 3: Taxa de presença
    query3 = """
        SELECT presencas_nominais, taxa_assiduidade
        FROM taxa_presenca t
        WHERE t.fk_deputado = %s
    """
    
    # Query 4: Total de proposições
    query4 = """
        SELECT COUNT(*) AS total_proposicao
        FROM proposicao_deputados p
        WHERE p.fk_deputado = %s
    """
    
    # Query 5: Proposições detalhes
    query5 = """
        SELECT p.cd_proposicoes, p.keywords, p.nome
        FROM proposicao_deputados pd
        INNER JOIN proposicoes p ON pd.fk_proposicao = p.cd_proposicoes
        WHERE pd.fk_deputado = %s
    """
    
    # Query 6: Despesas por tipo
    query6 = """
        SELECT d.tipo, d.gasto_total
        FROM despesas d
        WHERE d.fk_deputado = %s
        ORDER BY d.gasto_total DESC
    """
    
    # Query 7: Discursos
    query7 = """
        SELECT d.tipo, d.transcricao AS texto, d.titulo, d.keywords, d.data_inicio
        FROM discursos d
        WHERE d.fk_deputado = %s
        ORDER BY d.data_inicio DESC
    """
    
    # Query 8: Proposições aprovadas
    query8 = """
        SELECT p.nome, p.status
        FROM proposicoes p
        INNER JOIN proposicao_deputados pd ON pd.fk_proposicao = p.cd_proposicoes
        WHERE pd.fk_deputado = %s AND (p.status = 'Transformado em Norma Jurídica' or p.status = 'Mapeamento Histórico / Concluída com sucesso' or p.status = 'Mapeamento Histórico / Aprovada' or p.status = 'Transformado em Norma Jurídica' or p.status = 'Transformado em nova proposição')
    """
    
    # Query 9: Média de presença e gasto
    query9 = """
        SELECT ROUND(AVG(t.taxa_assiduidade), 2) AS presenca
        FROM taxa_presenca t
    """

    # Query 10: Média de gasto
    query10 = """
        SELECT ROUND(AVG(e.despesa_total), 2) AS gasto
        FROM economia e
    """
    
    cursor.execute(query1, (id,))
    deputado = cursor.fetchone()

    cursor.execute(query2, (id,))
    gasto = cursor.fetchone()

    cursor.execute(query3, (id,))
    presenca = cursor.fetchone()

    cursor.execute(query4, (id,))
    total_proposicao = cursor.fetchone()

    cursor.execute(query5, (id,))
    proposicoes = cursor.fetchall()

    cursor.execute(query6, (id,))
    despesas = cursor.fetchall()

    cursor.execute(query7, (id,))
    discursos = cursor.fetchall()

    cursor.execute(query8, (id,))
    aprovadas = cursor.fetchall()

    cursor.execute(query9)
    media_presenca = cursor.fetchone()

    cursor.execute(query10)
    media_gasto = cursor.fetchone()

    # Query 11: Combinar todas as métricas em uma única query
    query11 = """
        SELECT 
            (SELECT COUNT(*) FROM proposicao_deputados WHERE fk_deputado = %s) as total_deputado,
            (SELECT COUNT(fk_proposicao) / COUNT(DISTINCT fk_deputado) FROM proposicao_deputados) as media_camara,
            (SELECT COUNT(*) FROM proposicao_deputados pd 
             JOIN proposicoes p ON pd.fk_proposicao = p.cd_proposicoes
             WHERE pd.fk_deputado = %s AND p.status = 'Transformado em Norma Jurídica') as aprovados_deputado,
            (SELECT COUNT(pd.fk_proposicao) / COUNT(DISTINCT pd.fk_deputado) 
             FROM proposicao_deputados pd
             JOIN proposicoes p ON pd.fk_proposicao = p.cd_proposicoes
             WHERE p.status = 'Transformado em Norma Jurídica') as media_aprovados_camara
    """
    
    # Query 12: Temas dos projetos aprovados do deputado específico
    query12 = """
        SELECT 
            tp.tipo,
            SUM(CASE WHEN pd.fk_deputado = %s THEN 1 ELSE 0 END) as qtd_deputado,
            COUNT(p.cd_proposicoes) / COUNT(DISTINCT pd.fk_deputado) as media_tema
        FROM proposicao_deputados pd
        JOIN proposicoes p ON pd.fk_proposicao = p.cd_proposicoes
        JOIN tema_proposicoes pt ON p.cd_proposicoes = pt.id_proposicao
        JOIN top_temas tp ON pt.id_tema = tp.cd_tp_temas
        WHERE p.status = 'Transformado em Norma Jurídica'
        GROUP BY tp.tipo
        HAVING SUM(CASE WHEN pd.fk_deputado = %s THEN 1 ELSE 0 END) > 0
        ORDER BY qtd_deputado DESC
        LIMIT 5
    """
    query13 = """
        SELECT tp.nome 
        FROM deputado_tema d
        INNER JOIN tema_peso tp ON tp.cd_tema = d.fk_tema
        WHERE fk_deputado = %s
        ORDER BY d.qtd_proposicoes DESC
    """
    #query14 = """
    #     {
    #     "Gestão pública e política": [
    #         "Administração pública",
    #         "Processo legislativo e atuação parlamentar",
    #         "Finanças públicas e orçamento",
    #         "Política, partidos e eleições"
    #     ],
    #     "Direitos, justiça e cidadania": [
    #         "Direito constitucional",
    #         "Direito civil e processual civil",
    #         "Direito penal e processual penal",
    #         "Direito e justiça",
    #         "Direitos humanos e minorias",
    #         "Direito e defesa do consumidor"
    #     ],
    #     "Economia e desenvolvimento": [
    #         "Economia",
    #         "Indústria, comércio e serviços",
    #         "Relações internacionais e comércio exterior",
    #         "Turismo",
    #         "Trabalho e emprego",
    #         "Previdência e assistência social"
    #     ],
    #     "Infraestrutura e tecnologia": [
    #         "Cidades e desenvolvimento urbano",
    #         "Viação, transporte e mobilidade",
    #         "Energia, recursos hídricos e minerais",
    #         "Comunicações"
    #     ],
    #     "Natureza e produção": [
    #         "Meio ambiente e desenvolvimento sustentável",
    #         "Agricultura, pecuária, pesca e extrativismo",
    #         "Estrutura fundiária"
    #     ],
    #     "Ciências": [
    #         "Ciências sociais e humanas",
    #         "Ciências exatas e da terra",
    #         "Ciência, tecnologia e inovação"
    #     ],
    #     "Saúde e educação": [
    #         "Saúde",
    #         "Educação"
    #     ],
    #     "Cultura, lazer e segurança": [
    #         "Arte, cultura e religião",
    #         "Esporte e lazer",
    #         "Defesa e segurança",
    #         "Homenagens e datas comemorativas"
    #     ]
    # }
    #"""
    
    query15 = """
        SELECT
        d.score_final as nota
        FROM desempenho d
        WHERE fk_deputado = %s
    
    """
    
    cursor.execute(query11, (id, id))
    stats = cursor.fetchone()
    
    cursor.execute(query15, (id,))
    score_final = cursor.fetchone()
    
    total_deputado = stats['total_deputado'] or 0
    media_camara = stats['media_camara'] or 0
    aprovados_deputado = stats['aprovados_deputado'] or 0
    media_aprovados_camara = stats['media_aprovados_camara'] or 0
    
    cursor.execute(query12, (id, id))
    temas_com_media = cursor.fetchall()
    
    labels_tema = []
    valores_dep_tema = []
    valores_med_tema = []
    
    for tema in temas_com_media:
        labels_tema.append(tema['tipo'])
        valores_dep_tema.append(tema['qtd_deputado'])
        valores_med_tema.append(round(tema['media_tema'], 1))

    cursor.execute(query13, (id,))
    temas_discursos = cursor.fetchall()
    
    # --- GERAÇÃO DOS GRÁFICOS ---
    grafico_proposicoes_img = gerar_grafico_deputado(
        total_deputado, round(media_camara, 1), 'Total de Projetos Propostos'
    )
    
    grafico_aprovados_img = gerar_grafico_deputado(
        aprovados_deputado, round(media_aprovados_camara, 1), 'Projetos Aprovados'
    )
    
    grafico_temas_img = gerar_grafico_temas(
        labels_tema, valores_dep_tema, valores_med_tema, 'Aprovados vs Média por Tema (Top 5)'
    )
    
    cursor.execute("""
    SELECT nome,imagem_deputado
    FROM deputado
    ORDER BY nome
    """)

    todos_deputados = cursor.fetchall()

    cursor.close()
    conn.close()

    for discurso in discursos:
        dt = datetime.fromisoformat(discurso['data_inicio'])
        discurso['data'] = dt.strftime('%d/%m/%Y')
        discurso['hora'] = dt.strftime('%H:%M')
    
    if deputado:
        return render_template("deputado.html", dep=deputado, gasto=gasto, presenca=presenca,total_proposicao=total_proposicao, proposicoes=proposicoes,grafico_proposicoes=grafico_proposicoes_img,grafico_aprovados=grafico_aprovados_img,grafico_temas=grafico_temas_img, despesas=despesas, discursos=discursos, aprovadas=aprovadas, media_presenca=media_presenca, media_gasto=media_gasto,todos_deputados=todos_deputados, temas_discursos=temas_discursos, score_final=score_final, nb=2)
    else:
        return {"erro": "Deputado não encontrado"}, 404


def remover_acentos(texto):
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

@route_bp.route('/buscar')
def buscar():
    estado = request.args.get('estado', '')
    partido = request.args.get('partido', '')
    
    filtros = []
    params = []
    
    if estado:
        filtros.append("e.uf = %s")
        params.append(estado)
    if partido:
        filtros.append("p.abreviacao = %s")
        params.append(partido)
    
    where_clause = "WHERE " + " AND ".join(filtros) if filtros else ""
    
    conexao = conectar()
    cursor = conexao.cursor(dictionary=True)
    
    # Usando GROUP BY para garantir que cada nome apareça apenas uma vez

    query = f"""
    SELECT d.cd_deputado, d.nome, d.nome_eleitoral, d.imagem_deputado,
           e.uf AS estado, p.abreviacao AS partido
    FROM deputado d
    JOIN estado e ON d.fk_estado = e.cd_estado
    JOIN partido p ON d.fk_partido = p.cd_partido
    {where_clause}
    GROUP BY d.cd_deputado, d.nome, d.nome_eleitoral, d.imagem_deputado, e.uf, p.abreviacao
    ORDER BY d.nome_eleitoral
    """

    cursor.execute(query, params)
    resultados = cursor.fetchall()
    
    cursor.close()
    conexao.close()
    
    return render_template("deputados.html", deputados=resultados, estados=estados, estado=estado, partido=partido, partidos=partidos, sticky_navbar=True, nb=2)


@route_bp.route('/procurar')
def procurar():
    estado   = request.args.get('estado', '').strip()
    partido  = request.args.get('partido', '').strip()
    pesquisa = request.args.get('pesquisa', '').strip()

    filtros = []
    params  = []

    if pesquisa:
        pesquisa_limpa = remover_acentos(pesquisa).lower()
        termo = f"%{pesquisa_limpa}%"
        filtros.append("(LOWER(d.nome) LIKE %s OR LOWER(d.nome_eleitoral) LIKE %s)")
        params.extend([termo, termo])

    if estado:
        filtros.append("e.uf = %s")
        params.append(estado)
    if partido:
        filtros.append("p.abreviacao = %s")
        params.append(partido)

    where_clause = "WHERE " + " AND ".join(filtros) if filtros else ""

    conexao = conectar()
    cursor  = conexao.cursor(dictionary=True)

    query = f"""
    SELECT DISTINCT d.cd_deputado, d.nome, d.nome_eleitoral, d.imagem_deputado,
           e.uf AS estado, p.abreviacao AS partido
    FROM deputado d
    JOIN estado e ON d.fk_estado = e.cd_estado
    JOIN partido p ON d.fk_partido = p.cd_partido
    {where_clause}
    ORDER BY d.nome_eleitoral
    """
    cursor.execute(query, params)
    resultados = cursor.fetchall()

    cursor.close()
    conexao.close()

    return render_template("deputados.html", deputados=resultados, estados=estados, estado=estado, partido=partido, partidos=partidos, pesquisa=pesquisa, sticky_navbar=True, nb=2)

#start
@route_bp.route("/api/filtros-dinamicos")
def filtros_dinamicos():
    conn = conectar()
    estado_selecionado = request.args.get('estado', '')
    partido_selecionado = request.args.get('partido', '')

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    # 2. Query de Estados (Passando por deputado para chegar no partido)
    query_estados = """
        SELECT DISTINCT e.uf 
        FROM estado e 
        JOIN deputado d ON e.cd_estado = d.fk_estado
        JOIN partido p ON d.fk_partido = p.cd_partido
    """
    params_estados = []
    # Se o usuário escolheu um partido na tela, filtramos os estados que têm deputados desse partido
    if partido_selecionado:
        query_estados += " WHERE p.abreviacao = %s"
        params_estados.append(partido_selecionado)
        
    cursor.execute(query_estados, params_estados)
    estados_disponiveis = [row['uf'] for row in cursor.fetchall()]

    # 3. Query de Partidos (Passando por deputado para chegar no estado)
    query_partidos = """
        SELECT DISTINCT p.abreviacao 
        FROM partido p 
        JOIN deputado d ON p.cd_partido = d.fk_partido
        JOIN estado e ON d.fk_estado = e.cd_estado
    """
    params_partidos = []
    # Se o usuário escolheu um estado na tela, filtramos os partidos que têm deputados nesse estado
    if estado_selecionado:
        query_partidos += " WHERE e.uf = %s"
        params_partidos.append(estado_selecionado)

    cursor.execute(query_partidos, params_partidos)
    partidos_disponiveis = [row['abreviacao'] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    # 4. Retorna a resposta para o JavaScript
    return jsonify({
        'estados': estados_disponiveis,
        'partidos': partidos_disponiveis
    })


#PÁGINA "SOBRE"
@route_bp.route('/sobre')
def sobre():
    return render_template('sobre.html', hide_pesquisa=True, nb=1)

#AUTOCOMPLETE
@route_bp.route('/autocomplete')
def autocomplete():
    q = request.args.get('pesquisa', '').strip()

    if len(q) < 2:
        return jsonify([])

    termo = f"%{remover_acentos(q).lower()}%"

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT d.cd_deputado AS id,
               d.nome_eleitoral,
               d.nome AS nome_civil,
               d.imagem_deputado AS foto_url
        FROM deputado d
        WHERE LOWER(d.nome_eleitoral) LIKE %s
           OR LOWER(d.nome) LIKE %s
        ORDER BY d.nome_eleitoral
        LIMIT 6
    """, (termo, termo))

    resultados = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(resultados)

#PÁGINA RANKING
@route_bp.route('/ranking')
def ranking():
    estado = request.args.get('estado', '')
    partido = request.args.get('partido', '')

    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            des.ranking,
            des.score_final * 10 AS score_final,
            d.cd_deputado AS id,
            d.nome_eleitoral,      
            d.nome AS nome_civil,
            d.imagem_deputado AS foto_url,
            e.uf AS estado,
            p.abreviacao AS partido
        FROM deputado d
        JOIN desempenho des ON des.fk_deputado = d.cd_deputado
        JOIN estado e ON d.fk_estado = e.cd_estado
        JOIN partido p ON d.fk_partido = p.cd_partido
        WHERE 1=1
    """
    params = []

    if estado:
        query += " AND e.uf = %s"
        params.append(estado)
    if partido:
        query += " AND p.abreviacao = %s"
        params.append(partido)

    query += " ORDER BY des.score_final DESC"

    cursor.execute(query, params)
    ranking_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('ranking.html', ranking=ranking_data, estado=estado, partido=partido)
@route_bp.route('/rankingf')
def rankingf():
    return render_template('rankingfront.html')
