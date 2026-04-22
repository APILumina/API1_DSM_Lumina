import mysql.connector
    
def conectar():
    return mysql.connector.connect(
        host = "serverless-europe-west3.sysp0000.db2.skysql.com",
        user = "dbpgf32109072",
        password = "6P08I94}Pehojl96x-pm1Hyfq",
        database = "LUMINA",
        port = 4050
    )