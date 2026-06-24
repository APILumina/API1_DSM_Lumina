from dotenv import load_dotenv  # Removido o load_model
import os

load_dotenv()

import mysql.connector

def conectar():
    # O os.environ.get('NOME') busca o valor lá do seu arquivo .env
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_ROOT_PASSWORD"), # <-- Ajustado para o nome certo do seu .env
        database=os.environ.get("DB_NAME"),
        port=int(os.environ.get("DB_PORT", 3306)), 
        use_pure=True
    )