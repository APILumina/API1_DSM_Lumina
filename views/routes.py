from flask import Blueprint, render_template
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
    return render_template("deputados.html")

@route_bp.route("/deputado")
def infodeputados():
    return render_template("deputado.html")

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
    
    cursor.execute("SELECT * FROM deputado")
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

