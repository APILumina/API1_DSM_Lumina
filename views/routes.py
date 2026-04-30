from flask import Blueprint, render_template,request,jsonify
import mysql
from database import conectar
import unicodedata

route_bp = Blueprint("route",__name__)

partidos = ["PT","PL","PSDB","PP","PRD","PDT","PSB","PSD","PSOL","REPUBLICANOS","AVANTE","MDB","UNIAO","PV","PCdoB","REDE","NOVO"]

# Lista de dicionários
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

@route_bp.route("/")
def home():
    return render_template ("index.html", partidos = sorted(partidos))

@route_bp.route("/graficos")
def graficos():
    return render_template("graficos.html")

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
    
    return render_template("deputados.html", deputados=dados, estado=estado, partido=partido, partidos = sorted(partidos))

from flask import jsonify, request

@route_bp.route("/dados/deputados")
def dados_deputados():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    
    page = int(request.args.get('page', 1))
    estado = request.args.get('estado', '')
    partido = request.args.get('partido', '')
    
    itens_por_pagina = 24
    offset = (page - 1) * itens_por_pagina
    
    filtros = []
    params = []
    
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

    query = """
    SELECT 
        d.cd_deputado,
        d.nome,
        d.nome_eleitoral,
        d.email,
        d.imagem_deputado,
        e.uf AS estado,
        p.abreviacao AS partido
        FROM deputado d
        JOIN estado e ON fk_estado = e.cd_estado
        JOIN partido p ON fk_partido = p.cd_partido
        WHERE d.cd_deputado = %s
    """
    query2 = """
    SELECT 
    COALESCE(SUM(CAST(REPLACE(g.gasto_total, ',', '.') AS DECIMAL(10,2))), 0) AS total
    FROM despesas g
    WHERE g.fk_deputado = %s
    """
    
    query3 = """
    SELECT presencas_nominais, taxa_assiduidade
    FROM taxa_presenca t
    WHERE t.fk_deputado = %s
    """
    
    query4 = """
    SELECT COUNT(*) AS total_proposicao
    FROM proposicao_deputados p
    WHERE p.fk_deputado = %s
    """
    
    query5 = """
    SELECT p.cd_proposicoes, p.keywords
    FROM proposicao_deputados pd
    INNER JOIN proposicoes p ON pd.fk_proposicao = p.cd_proposicoes
    WHERE pd.fk_deputado = %s
    AND p.keywords IS NOT NULL
    AND p.keywords <> 'None' LIMIT 5
    """
    

    cursor.execute(query, (id,))
    deputado = cursor.fetchone()
    
    cursor.execute(query2,(id,))
    gasto = cursor.fetchone()
    
    cursor.execute(query3,(id,))
    presenca = cursor.fetchone()
    
    cursor.execute(query4,(id,))
    total_proposicao = cursor.fetchone()
    
    cursor.execute(query5,(id,))
    proposicoes = cursor.fetchall()

    cursor.close()
    conn.close()

    if deputado:
        return render_template("deputado.html", dep=deputado, gasto = gasto, presenca = presenca, total_proposicao = total_proposicao, proposicoes = proposicoes)
    else:
        return {"erro": "Deputado não encontrado"}, 404

@route_bp.route("/graficos/estado")
def estado():
    
    for e in estados:
        e['img'] = f"img/estados/{e['uf'].lower()}.png"
        e['link'] = f"partido/{e['uf'].lower()}"
        e['alt'] = e['uf']
        e['texto'] = e['nome']
    
    return render_template("escolha-estados.html", lista=estados)

@route_bp.route("/graficos/partido/<uf>")
def partido(uf):
    
    partido_lista = []
    nome_estado = False
    
    for e in estados:
        if e['uf'].lower() == uf.lower():
            nome_estado = e['nome']
            break
    
    if not nome_estado:
        return {"erro": f"Estado não encontrado"}, 404
    
    for p in sorted(partidos):
        dicionario = {
            'img' : f"img/partidos/{p.lower()}.png",
            'link' : f"#",
            'alt' : p,
            'texto' : p
        }
        partido_lista.append(dicionario)

    return render_template("escolha-partido.html", lista=partido_lista, estado=nome_estado)

def remover_acentos(texto):
    # Normaliza para a forma NFKD (separa o caractere do acento)
    nfkd_form = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


@route_bp.route('/procurar')
def procurar():
    estado   = request.args.get('estado', '').strip()
    partido  = request.args.get('partido', '').strip()
    pesquisa = request.args.get('pesquisa', '').strip()

    filtros = []
    params  = []

    # Filtro de texto (search bar)
    if pesquisa:
        pesquisa_limpa = remover_acentos(pesquisa).lower()
        termo = f"%{pesquisa_limpa}%"
        filtros.append("(d.nome LIKE %s OR d.nome_eleitoral LIKE %s)")
        params.extend([termo, termo])

    # Filtros de estado e partido
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

    return render_template('deputados.html', deputados=resultados, estado=estado, partido=partido, pesquisa=pesquisa, partidos = sorted(partidos))