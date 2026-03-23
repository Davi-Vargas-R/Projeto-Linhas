import sqlite3
#Função só pra eu não ter que colocar esse trecho de definir conexão toda hora
def conectar():
    conn=sqlite3.connect("linhas.db")
    return conn
