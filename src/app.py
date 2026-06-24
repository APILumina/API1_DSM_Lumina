from flask import Flask,render_template
from src.views.routes import route_bp
import unicodedata

app = Flask(__name__)
app.jinja_env.globals.update(zip=zip)
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

@app.context_processor
def inject_globals():
    """Adiciona variáveis globais disponíveis em todos os templates"""
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
    
    return dict(partidos=partidos, estados=estados)

@app.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        # Define o cache para 1 ano (31536000 segundos)
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response

app.jinja_env.filters['real'] = formato_moeda
app.jinja_env.filters['porcentagem'] = formato_porcentagem
app.jinja_env.filters['sem_acentos'] = remover_acentos

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)


