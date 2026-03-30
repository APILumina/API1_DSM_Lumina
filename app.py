from flask import Flask
from views.graphs import graficos_bp

app = Flask(__name__)
app.register_blueprint(graficos_bp)

if __name__ == "__main__":
    app.run(debug=True)