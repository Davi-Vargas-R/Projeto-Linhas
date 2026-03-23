from datetime import datetime
from database.conexao import conectar
import pandas as pd

#Ele cria o df do estado atual do banco para ser utilizado para comparar com a planilha corretamente
def carregar_relacoes():
    conn = conectar()

    df = pd.read_sql_query("""
    SELECT 
        ul.id_usuario,
        ul.id_linha,
        ul.valor_linha,
        ul.status_linha,
        u.usuario,
        l.msisdn
    FROM usuarios_linhas ul
    LEFT JOIN usuarios u ON ul.id_usuario = u.id_usuario
    LEFT JOIN linhas l ON ul.id_linha = l.id_linha
    WHERE ul.status_ativo = 1
    """, conn)

    conn.close()
    return df


#Verifica se o usuario já existe no banco
def buscar_usuario_por_nome(usuario):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id_usuario FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()

    conn.close()
    return resultado[0] if resultado else None

#Verifica se o msisdn já existe no banco
def buscar_linha_por_msisdn(msisdn):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id_linha FROM linhas WHERE msisdn = ?", (msisdn,))
    resultado = cursor.fetchone()

    conn.close()
    return resultado[0] if resultado else None
