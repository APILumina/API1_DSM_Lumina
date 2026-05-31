import os
import mysql.connector

def conectar():
    # O os.environ.get('NOME') busca o valor lá do seu arquivo .env
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME"),
        port=int(os.environ.get("DB_PORT", 3306)), # Converte para número e usa 3306 como padrão
        use_pure=True
    )