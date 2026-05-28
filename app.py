from flask import Flask,render_template
from views.routes import route_bp
import unicodedata

app = Flask(__name__)
app.register_blueprint(route_bp)

def formato_moeda(valor):
    try:
        v = "{:,.2f}".format(float(valor))
        return v.replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return valor

def formato_porcentagem(valor):
    try:
        v = "{:.1f}".format(float(valor))
        
        return v.replace('.', ',')
    except (ValueError, TypeError):
        return valor
    

def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    ).lower()

app.jinja_env.filters['real'] = formato_moeda
app.jinja_env.filters['porcentagem'] = formato_porcentagem
app.jinja_env.filters['sem_acentos'] = remover_acentos

if __name__ == "__main__":
    app.run(debug=True)


