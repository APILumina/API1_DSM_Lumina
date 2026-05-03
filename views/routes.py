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

partidos = ["PT","PL","PSDB","PP","PRD","PDT","PSB","PSD","PSOL","REPUBLICANOS","AVANTE","MDB","UNIAO","PV","PCdoB","REDE","NOVO"]

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


def gerar_grafico_deputado(valor_deputado, valor_media, titulo):
    # Ajustado para o mesmo tamanho do gráfico de temas
    fig, ax = plt.subplots(figsize=(6, 6)) 
    
    cores = ['#1A249D', "#3c66ef"]
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


@route_bp.route("/")
def home():
    return render_template("index.html", partidos=sorted(partidos), hide_pesquisa=True, sticky_navbar=True)


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
            JOIN deputado d ON pd.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido   = p.cd_partido
            JOIN estado e   ON d.fk_estado    = e.cd_estado
            WHERE p.abreviacao = %s
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
            JOIN deputado d ON pd.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido   = p.cd_partido
            JOIN estado e   ON d.fk_estado    = e.cd_estado
            WHERE e.uf = %s AND p.abreviacao = %s
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
            SELECT p.abreviacao AS label, COUNT(*) AS total
            FROM proposicao_deputados pd
            JOIN deputado d ON pd.fk_deputado = d.cd_deputado
            JOIN partido p  ON d.fk_partido   = p.cd_partido
            GROUP BY p.abreviacao ORDER BY total DESC
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

    cursor.close()
    conn.close()

    return render_template("graficos.html",
        estado=estado,
        partido=partido,
        partidos=sorted(partidos),
        grafico_projetos=grafico_projetos,
        grafico_presenca=grafico_presenca,
        grafico_gastos=grafico_gastos,
    )


@route_bp.route("/deputados")
def deputados():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    estado  = request.args.get('estado', '')
    partido = request.args.get('partido', '')

    filtros = []
    params  = []

    if estado:
        filtros.append("e.uf = %s")
        params.append(estado)
    if partido:
        filtros.append("p.abreviacao = %s")
        params.append(partido)

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
    {where}
    ORDER BY d.nome_eleitoral
    LIMIT 24 OFFSET 0
    """

    cursor.execute(query, params)
    dados = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("deputados.html", deputados=dados, estado=estado, partido=partido, partidos=sorted(partidos), sticky_navbar=True)


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
        SELECT p.nome
        FROM proposicoes p
        INNER JOIN proposicao_deputados pd ON pd.fk_proposicao = p.cd_proposicoes
        WHERE pd.fk_deputado = %s AND p.status = 'Transformado em Norma Jurídica'
    """
    
    # Query 9: Média de presença e gasto
    query9 = """
        SELECT ROUND(AVG(t.presencas_nominais), 2) AS presenca
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



    def gerar_grafico_temas(labels, valores_deputado, valores_media, titulo):
        fig, ax = plt.subplots(figsize=(6, 6)) 
        if not labels:
            ax.text(0.5, 0.5, 'Nenhum projeto aprovado associado a um tema.', 
                    ha='center', va='center', fontsize=12, color='#081638')
            ax.axis('off')
        else:
            x = range(len(labels))
            width = 0.35 
            x_dep = [pos - width/2 for pos in x]
            x_med = [pos + width/2 for pos in x]
            ax.bar(x_dep, valores_deputado, width, label='Este Deputado', color='#1A249D')
            ax.bar(x_med, valores_media, width, label='Média da Câmara', color='#efc33c')
            ax.set_title(titulo, pad=15, fontsize=12, fontweight='bold', color='#081638')
            ax.set_xticks(list(x))
            ax.set_xticklabels(labels, rotation=90, ha='center', fontsize=9)
            ax.legend()
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_color('#cccccc')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True, dpi=100)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    
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
    
    # Query 12: Temas dos projetos aprovados - eliminar N+1
    query12 = """
        SELECT 
            tp.nome,
            COUNT(p.cd_proposicoes) as qtd_deputado,
            COUNT(p.cd_proposicoes) / COUNT(DISTINCT pd.fk_deputado) as media_tema
        FROM proposicao_deputados pd
        JOIN proposicoes p ON pd.fk_proposicao = p.cd_proposicoes
        JOIN proposicao_tema pt ON p.cd_proposicoes = pt.id_proposicao
        JOIN tema_proposicoes tp ON pt.id_tema = tp.cd_tema
        WHERE p.status = 'Transformado em Norma Jurídica'
        GROUP BY tp.nome
        ORDER BY (
            SELECT COUNT(p2.cd_proposicoes)
            FROM proposicao_deputados pd2
            JOIN proposicoes p2 ON pd2.fk_proposicao = p2.cd_proposicoes
            JOIN proposicao_tema pt2 ON p2.cd_proposicoes = pt2.id_proposicao
            JOIN tema_proposicoes tp2 ON pt2.id_tema = tp2.cd_tema
            WHERE pd2.fk_deputado = %s AND p2.status = 'Transformado em Norma Jurídica' AND tp2.nome = tp.nome
        ) DESC
        LIMIT 5
    """
    
    cursor.execute(query11, (id, id))
    stats = cursor.fetchone()
    
    total_deputado = stats['total_deputado'] or 0
    media_camara = stats['media_camara'] or 0
    aprovados_deputado = stats['aprovados_deputado'] or 0
    media_aprovados_camara = stats['media_aprovados_camara'] or 0
    
    cursor.execute(query12, (id,))
    temas_com_media = cursor.fetchall()
    
    labels_tema = []
    valores_dep_tema = []
    valores_med_tema = []
    
    for tema in temas_com_media:
        labels_tema.append(tema['nome'])
        valores_dep_tema.append(tema['qtd_deputado'])
        valores_med_tema.append(round(tema['media_tema'], 1))
    
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

    cursor.close()
    conn.close()

    for discurso in discursos:
        dt = datetime.fromisoformat(discurso['data_inicio'])
        discurso['data'] = dt.strftime('%d/%m/%Y')
        discurso['hora'] = dt.strftime('%H:%M')

    if deputado:
        return render_template("deputado.html", dep=deputado, gasto=gasto, presenca=presenca,total_proposicao=total_proposicao, proposicoes=proposicoes,grafico_proposicoes=grafico_proposicoes_img,grafico_aprovados=grafico_aprovados_img,grafico_temas=grafico_temas_img, despesas=despesas, discursos=discursos, aprovadas=aprovadas, media_presenca=media_presenca, media_gasto=media_gasto)
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
    
    return render_template('deputados.html', deputados=resultados, estado=estado, partido=partido)


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
        filtros.append("(d.nome LIKE %s OR d.nome_eleitoral LIKE %s)")
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

    return render_template('deputados.html', deputados=resultados, estado=estado,
                           partido=partido, pesquisa=pesquisa, partidos=sorted(partidos))


@route_bp.route('/estados')
def lista_estados():
    return render_template('estado.html')


@route_bp.route('/estado_detalhe/<uf>')
def estado_detalhe(uf):
    conn = conectar()

    query = """
        SELECT p.abreviacao AS partido, SUM(d.gasto_total) AS total_gasto
        FROM despesas d
        JOIN estado e ON d.fk_estado = e.cd_estado
        JOIN partido p ON d.fk_partido = p.cd_partido
        WHERE e.uf = %s
        GROUP BY p.abreviacao
        ORDER BY total_gasto DESC
    """

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (uf.upper(),))
        rows = cursor.fetchall()
        df = pd.DataFrame(rows)
        cursor.close()
    finally:
        conn.close()

    grafico_url = gerar_grafico(df, 'partido', 'total_gasto', f'Ranking de Gastos por Partido - {uf.upper()}')

    return render_template('estados_detalhes.html', uf=uf.upper(), grafico_url=grafico_url)