from flask import Blueprint, render_template,request,jsonify
import mysql
from database import conectar

route_bp = Blueprint("route",__name__)

@route_bp.route("/")
def home():
    return render_template ("index.html")

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
    
    return render_template("deputados.html", deputados=dados, estado=estado, partido=partido)

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
    SELECT COUNT(*) AS total_presencas
    FROM presencas f 
    WHERE f.fk_deputado = %s
    """
    
    query4 = """
    SELECT COUNT(*) AS total_proposicao
    FROM proposicao_deputados p
    WHERE p.fk_deputado = %s
    """
    
    query5 = """
    SELECT p.cd_proposicoes, p.nome
    FROM proposicao_deputados pd
    INNER JOIN proposicoes p ON pd.fk_proposicao = p.cd_proposicoes
    WHERE pd.fk_deputado = %s;
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
    proposicao = cursor.fetchall()

    cursor.close()
    conn.close()

    if deputado:
        return render_template("deputado.html", dep=deputado, gasto = gasto, presenca = presenca, total_proposicao = total_proposicao, proposicao = proposicao)
    else:
        return {"erro": "Deputado não encontrado"}, 404

@route_bp.route("/estado")
def estado():
    return render_template("deputados-estados.html")

@route_bp.route("/partido")
def partido():
    return render_template("escolha-partido.html")

@route_bp.route("/tudo")
def tudo():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM deputado WHERE nome LIKE 'Arlindo%'")
    dados = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template("teste.html", deputados=dados)

@route_bp.route("/tudo/<int:id>")
def deputado_por_id(id):
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

    cursor.execute(query, (id,))
    deputado = cursor.fetchone()

    cursor.close()
    conn.close()

    if deputado:
        return render_template("teste.html", dep=deputado)
    else:
        return {"erro": "Deputado não encontrado"}, 404

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
    SELECT ANY_VALUE(d.cd_deputado) as cd_deputado, 
           d.nome_eleitoral, 
           ANY_VALUE(d.nome) as nome,
           ANY_VALUE(d.imagem_deputado) as imagem_deputado,
           ANY_VALUE(e.uf) AS estado, 
           ANY_VALUE(p.abreviacao) AS partido
            FROM deputado d
            JOIN estado e ON d.fk_estado = e.cd_estado
            JOIN partido p ON d.fk_partido = p.cd_partido
            {where_clause}
            GROUP BY d.nome_eleitoral
            ORDER BY d.nome_eleitoral
            """

    cursor.execute(query, params)
    resultados = cursor.fetchall()
    
    cursor.close()
    conexao.close()
    
    return render_template('deputados.html', deputados=resultados, estado=estado, partido=partido)