from flask import Flask,render_template
from views.routes import route_bp

app = Flask(__name__)
app.register_blueprint(route_bp)

def formato_moeda(valor):
    try:
        v = "{:,.2f}".format(float(valor))
        return v.replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return valor

app.jinja_env.filters['real'] = formato_moeda

if __name__ == "__main__":
    app.run(debug=True)


