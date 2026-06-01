from flask import Blueprint, render_template, request, jsonify, url_for
import mysql
from src.database import conectar
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
    {'abreviacao': 'CIDADANIA', 'nome': 'Cidadania'},
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

Temas = [
    {
        "Gestão pública e política": [
            ["Administração pública", 34],
            ["Processo legislativo e atuação parlamentar", 52],
            ["Finanças públicas e orçamento", 70],
            ["Política, partidos e eleições", 74]
        ],

        "Direitos, justiça e cidadania": [
            ["Direito constitucional", 68],
            ["Direito civil e processual civil", 42],
            ["Direito penal e processual penal", 43],
            ["Direito e justiça", 76],
            ["Direitos humanos e minorias", 44],
            ["Direito e defesa do consumidor", 67]
        ],

        "Economia e desenvolvimento": [
            ["Economia", 40],
            ["Indústria, comércio e serviços", 66],
            ["Relações internacionais e comércio exterior", 55],
            ["Turismo", 60],
            ["Trabalho e emprego", 58],
            ["Previdência e assistência social", 51]
        ],

        "Infraestrutura e tecnologia": [
            ["Cidades e desenvolvimento urbano", 41],
            ["Viação, transporte e mobilidade", 61],
            ["Energia, recursos hídricos e minerais", 54],
            ["Comunicações", 37]
        ],

        "Natureza e produção": [
            ["Meio ambiente e desenvolvimento sustentável", 48],
            ["Agricultura, pecuária, pesca e extrativismo", 64],
            ["Estrutura fundiária", 49]
        ],

        "Ciências": [
            ["Ciências sociais e humanas", 86],
            ["Ciências exatas e da terra", 85],
            ["Ciência, tecnologia e inovação", 62]
        ],

        "Saúde e educação": [
            ["Saúde", 56],
            ["Educação", 46]
        ],

        "Cultura, lazer e segurança": [
            ["Arte, cultura e religião", 35],
            ["Esporte e lazer", 39],
            ["Defesa e segurança", 57],
            ["Homenagens e datas comemorativas", 72]
        ]
    }
]

situacoes_projetos = {
    "Aprovado": {
        "codigos": [98, 114, 1140, 1230],
        "ordem": 1,
        "label": "Aprovado",
        "cor": "green"
    },
    
    "Em Votação": {
        "codigos": [1150, 1160, 1200, 1201, 1210, 1220, 1221, 1223, 1294, 1300, 1301, 1302],
        "ordem": 2,
        "label": "Em votação",
        "cor": "teal"
    },
    
    "Preparação para Votação": {
        "codigos": [904, 910, 927, 929, 932, 1020, 1040, 1052, 1060, 1070, 1080, 1270, 1290, 1291],
        "ordem": 3,
        "label": "Preparação para votação",
        "cor": "orange"
    },
    
    "Estágio Avançado": {
        "codigos": [924],  # ✅ Só "Pronta para Pauta"
        "ordem": 4,
        "label": "Pronta para pauta",
        "cor": "sky"
    },
    
    "Enviado para Próximo Passo": {
        "codigos": [926, 1293, 1299, 1303, 1305],
        "ordem": 5,
        "label": "Enviado para próximo passo",
        "cor": "cyan"
    },
    
    "Aguardando Comissões": {
        "codigos": [901, 902, 906, 922, 1280, 1296],
        "ordem": 6,
        "label": "Aguardando comissões",
        "cor": "blue"
    },
    
    "Em Análise": {
        "codigos": [903, 915, 928, 1090, 1091, 1297, 1313, 1314, 1380],
        "ordem": 7,
        "label": "Em análise",
        "cor": "indigo"
    },
    
    "Aguardando Designação": {
        "codigos": [907, 911, 1170, 1185, 1180],
        "ordem": 8,
        "label": "Aguardando designação",
        "cor": "amber"
    },
    
    "Recém Protocolo": {
        "codigos": [900, 912, 917, 1383],
        "ordem": 9,
        "label": "Recém protocolo",
        "cor": "gray"
    },
    
    "Rejeitado ou Devolvido": {
        "codigos": [937, 939, 941, 950, 1222, 1292],
        "ordem": 10,
        "label": "Rejeitado ou devolvido",
        "cor": "red"
    },
    
    "Arquivado": {
        "codigos": [923, 931, 940, 1250, 1260, 1360],
        "ordem": 11,
        "label": "Arquivado",
        "cor": "slate"
    },
    
    "Processos Especiais": {
        "codigos": [1310, 1311, 1312, 1350, 1355, 1381, 1382, 1298],
        "ordem": 12,
        "label": "Processo especial (Ética)",
        "cor": "rose"
    }
}

def obter_ordem_situacao(codigo_situacao):
    """Retorna a ordem de classificação para um código de situação"""
    for grupo in situacoes_projetos.values():
        if codigo_situacao in grupo['codigos']:
            return grupo['ordem']
    return 999

def obter_partidos_abreviados():
    return sorted([p['abreviacao'] for p in partidos])

def adicionar_info_grupo(proposicoes):
    """Adiciona informações de grupo, cor e label a cada proposição"""
    for prop in proposicoes:
        for grupo_nome, grupo_info in situacoes_projetos.items():
            if prop['status'] in grupo_info['codigos']:
                prop['grupo'] = grupo_nome
                prop['cor'] = grupo_info['cor']
                prop['label'] = grupo_info['label']
                break
        else:
            prop['grupo'] = 'Outro'
            prop['cor'] = 'gray'
            prop['label'] = 'Sem classificação'
    return proposicoes

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
            JOIN proposicoes pr ON pd.fk_proposicao = pr.cd_proposicoes
            WHERE e.uf = %s AND pr.status = 'Transformado em Norma Jurídica'
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

    page = int(request.args.get('page', 1))
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
        if tema.isdigit():
            filtros.append("""
                EXISTS (
                    SELECT 1 FROM deputado_tema dt
                    JOIN top_temas t ON t.cd_tp_temas = dt.fk_tema
                    WHERE dt.fk_deputado = d.cd_deputado
                    AND t.cd_tp_temas = %s
                )
            """)
            params.append(tema)
        else:
            codigos = []
            for tema_dict in Temas:
                if tema in tema_dict:
                    codigos = [item[1] for item in tema_dict[tema]]
                    break
            if codigos:
                placeholders = ','.join(['%s'] * len(codigos))
                filtros.append(f"""
                    EXISTS (
                        SELECT 1 FROM deputado_tema dt
                        JOIN top_temas t ON t.cd_tp_temas = dt.fk_tema
                        WHERE dt.fk_deputado = d.cd_deputado
                        AND t.cd_tp_temas IN ({placeholders})
                    )
                """)
                params.extend(codigos)

    where = ("WHERE " + " AND ".join(filtros)) if filtros else ""

    itens_por_pagina = 24
    offset = (page - 1) * itens_por_pagina

    query = f"""
    SELECT DISTINCT
        d.cd_deputado, d.nome, d.nome_eleitoral, d.imagem_deputado,
        e.uf AS estado, p.abreviacao AS partido
    FROM deputado d
    JOIN estado e ON d.fk_estado = e.cd_estado
    JOIN partido p ON d.fk_partido = p.cd_partido
    {joins}
    {where}
    ORDER BY d.nome_eleitoral
    LIMIT {itens_por_pagina} OFFSET {offset}
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
    ORDER BY tipo
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
        Temas=Temas,
        sticky_navbar=True,
        nb=2,
        page=page
    )

@route_bp.route("/dados/deputados")
def dados_deputados():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    page    = int(request.args.get('page', 1))
    estado  = request.args.get('estado', '')
    partido = request.args.get('partido', '')
    tema    = request.args.get('tema', '') 

    itens_por_pagina = 24
    offset = (page - 1) * itens_por_pagina

    filtros = []
    params  = []

    joins = "" 

    if estado and estado != 'Estado':
        filtros.append("e.uf = %s")
        params.append(estado)
    if partido and partido != 'Partido':
        filtros.append("p.abreviacao = %s")
        params.append(partido)
    if tema:
        if tema.isdigit():
            filtros.append("""
                EXISTS (
                    SELECT 1 FROM deputado_tema dt
                    JOIN top_temas t ON t.cd_tp_temas = dt.fk_tema
                    WHERE dt.fk_deputado = d.cd_deputado
                    AND t.cd_tp_temas = %s
                )
            """)
            params.append(tema)
        else:
            codigos = []
            for tema_dict in Temas:
                if tema in tema_dict:
                    codigos = [item[1] for item in tema_dict[tema]]
                    break
            if codigos:
                placeholders = ','.join(['%s'] * len(codigos))
                filtros.append(f"""
                    EXISTS (
                        SELECT 1 FROM deputado_tema dt
                        JOIN top_temas t ON t.cd_tp_temas = dt.fk_tema
                        WHERE dt.fk_deputado = d.cd_deputado
                        AND t.cd_tp_temas IN ({placeholders})
                    )
                """)
                params.extend(codigos)

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

    verificacaoRorN = "/ranking" in (request.referrer or "")

    # ═══════════════════════════════════════════════════════════
    # DEFINIÇÃO DE QUERIES
    # ═══════════════════════════════════════════════════════════
    
    # Query 1: Dados básicos do deputado
    query1 = """
        SELECT 
            d.cd_deputado as id, d.nome, d.nome_eleitoral, d.email, d.imagem_deputado,
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
        SELECT p.cd_proposicoes, p.keywords, p.nome, p.codSituacao as status
        FROM proposicao_deputados pd
        INNER JOIN proposicoes p ON pd.fk_proposicao = p.cd_proposicoes
        WHERE pd.fk_deputado = %s
        ORDER BY
            CASE
                WHEN p.codSituacao IN (98, 114, 1140, 1230) THEN 1
                WHEN p.codSituacao IN (1150, 1160, 1200, 1201, 1210, 1220, 1221, 1223, 1294, 1300, 1301, 1302) THEN 2
                WHEN p.codSituacao IN (904, 910, 927, 929, 932, 1020, 1040, 1052, 1060, 1070, 1080, 1270, 1290, 1291) THEN 3
                WHEN p.codSituacao IN (920, 924, 930, 1100, 1120) THEN 4
                WHEN p.codSituacao IN (926, 1293, 1299, 1303, 1305) THEN 5
                WHEN p.codSituacao IN (901, 902, 906, 922, 1280, 1296) THEN 6
                WHEN p.codSituacao IN (903, 915, 928, 1090, 1091, 1297, 1313, 1314, 1380) THEN 7
                WHEN p.codSituacao IN (907, 911, 1170, 1185, 1180) THEN 8
                WHEN p.codSituacao IN (900, 912, 917, 1383) THEN 9
                WHEN p.codSituacao IN (937, 939, 941, 950, 1222, 1292) THEN 10
                WHEN p.codSituacao IN (923, 931, 940, 1250, 1260, 1360) THEN 11
                WHEN p.codSituacao IN (1310, 1311, 1312, 1350, 1355, 1381, 1382, 1298) THEN 12
                ELSE 13
            END ASC,
            p.nome ASC;
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
        SELECT tp.nome, d.qtd_proposicoes as qtd
        FROM deputado_tema d
        INNER JOIN tema_peso tp ON tp.cd_tema = d.fk_tema
        WHERE fk_deputado = %s
        ORDER BY d.qtd_proposicoes DESC
    """
    
    query15 = """
        SELECT
            d.score_final as nota,
            d.ranking as posicao_ranking
        FROM desempenho d
        WHERE fk_deputado = %s
    
    """
    
    # Query 16: Quantidade de proposições aprovadas
    query16 = """
        SELECT COUNT(*) AS total
        FROM proposicoes p
        INNER JOIN proposicao_deputados pd ON pd.fk_proposicao = p.cd_proposicoes
        WHERE pd.fk_deputado = %s 
          AND p.codSituacao IN (
            98, 114, 1140, 1230
          )
    """
    
    # Query 17: Quantidade de proposições (quase) aprovadas
    query17 = """
        SELECT COUNT(*) AS total
        FROM proposicoes p
        INNER JOIN proposicao_deputados pd ON pd.fk_proposicao = p.cd_proposicoes
        WHERE pd.fk_deputado = %s 
          AND p.codSituacao IN (
              1150, 1160, 1200, 1201, 1210, 1220, 1221, 1223, 1294, 1300, 1301, 1302,
              904, 910, 927, 929, 932, 1020, 1040, 1052, 1060, 1070, 1080, 1270, 1290, 1291,
              924
          )
    """

    
    # Query 18: Situação do deputado
    query18 = """
        SELECT s.nome
        FROM situacao_deputado s
        WHERE s.fk_deputado = %s
    """
    
    # Query 19: Cargo do deputado
    query19 = """
        SELECT 
            GROUP_CONCAT(DISTINCT l.sigla_cargo SEPARATOR ' / ') as cargos,
            GROUP_CONCAT(l.cargo ORDER BY l.peso_cargo DESC SEPARATOR '|||') as cargos_extenso,
            GROUP_CONCAT(l.nome_orgao ORDER BY l.peso_cargo DESC SEPARATOR '|||') as orgaos
        FROM lideranca_orgaos l
        WHERE l.fk_deputado = %s
        AND l.sigla_cargo IS NOT NULL
    """
    # Query 20 Autorias
    query20 = """
	SELECT SUM(autor) AS autor
	FROM proposicao_deputados
	WHERE fk_deputado = %s
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
    proposicoes = adicionar_info_grupo(proposicoes)

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
    
    cursor.execute(query11, (id, id))
    stats = cursor.fetchone()
    
    cursor.execute(query12, (id, id))
    temas_com_media = cursor.fetchall()
    
    cursor.execute(query13, (id,))
    temas_discursos = cursor.fetchall()
    
    cursor.execute(query15, (id,))
    score_final = cursor.fetchone()
    
    cursor.execute(query16, (id,))
    prop_aprov = cursor.fetchone()
    
    cursor.execute(query17, (id,))
    prop_quase_aprov = cursor.fetchone()
    
    cursor.execute(query18, (id,))
    situacao = cursor.fetchone()
    
    cursor.execute(query19, (id,))
    cargo = cursor.fetchone()
    
    cursor.execute(query20, (id,))
    autoria = cursor.fetchone()
    
    total_deputado = stats['total_deputado'] or 0
    media_camara = stats['media_camara'] or 0
    aprovados_deputado = stats['aprovados_deputado'] or 0
    media_aprovados_camara = stats['media_aprovados_camara'] or 0
    
    labels_tema = []
    valores_dep_tema = []
    valores_med_tema = []
    
    for tema in temas_com_media:
        labels_tema.append(tema['tipo'])
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
        return render_template("deputado.html", dep=deputado, gasto=gasto, presenca=presenca,total_proposicao=total_proposicao, proposicoes=proposicoes,grafico_proposicoes=grafico_proposicoes_img,grafico_aprovados=grafico_aprovados_img,grafico_temas=grafico_temas_img, despesas=despesas, discursos=discursos, aprovadas=aprovadas, media_presenca=media_presenca, media_gasto=media_gasto,todos_deputados=todos_deputados, temas_discursos=temas_discursos, score_final=score_final, nb=2, prop_aprov=prop_aprov, prop_quase_aprov=prop_quase_aprov, situacao=situacao,autoria=autoria,verificacaoRorN=verificacaoRorN, cargo=cargo)
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

    query += " ORDER BY des.score_final DESC, des.ranking"

    cursor.execute(query, params)
    ranking_data = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('ranking.html', ranking=ranking_data, estado=estado, partido=partido, nb=3)
