from datetime import datetime
from database.conexao import conectar

#Função para adicionar usario no banco
def inserir_usuario(id_usuario, usuario):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO usuarios (id_usuario, usuario)
    VALUES (?, ?)
    """, (id_usuario, usuario))

    conn.commit()
    conn.close()


#Função para adicionar linha no banco
def inserir_linha(id_linha, msisdn):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO linhas (id_linha, msisdn)
    VALUES (?, ?)
    """, (id_linha, msisdn))

    conn.commit()
    conn.close()


#Verifica novamente se o usuário existe no banco, caso não, insere o usuário no banco e retorna o id dele
def obter_ou_criar_usuario(usuario):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id_usuario FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()

    if resultado:
        conn.close()
        return resultado[0]

    cursor.execute("INSERT INTO usuarios (usuario) VALUES (?)", (usuario,))
    conn.commit()

    novo_id = cursor.lastrowid
    conn.close()
    return novo_id


#Verifica novamente se o msisdn existe no banco, caso não, insere o msisdn no banco e retorna o id dele
def obter_ou_criar_linha(msisdn):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id_linha FROM linhas WHERE msisdn = ?", (msisdn,))
    resultado = cursor.fetchone()

    if resultado:
        conn.close()
        return resultado[0]

    cursor.execute("INSERT INTO linhas (msisdn) VALUES (?)", (msisdn,))
    conn.commit()

    novo_id = cursor.lastrowid
    conn.close()
    return novo_id
