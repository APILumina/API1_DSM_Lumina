import mysql.connector
    
def conectar():
    return mysql.connector.connect(
    host = "54.198.148.230",
    user = "root",
    password = "lumina1234",
    database = "Lumina2",
    port = 3306,
    use_pure = True
    )