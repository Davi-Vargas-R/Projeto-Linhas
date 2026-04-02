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

def registrar_gasto_mensal(mes,ano, valor_total):
    #Insere ou atualiza o gasto do mês e ano informado. Retornando 'inserido' ou 'atualizado' ou 'ignorado'
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, valor_total FROM gastos_mensais WHERE mes = ? AND ano = ?
                   """,(mes,ano))
    existente= cursor.fetchone()

    if existente:
        if existente[1] == valor_total:
            conn.close()
            return "ignorado"
        cursor.execute("""
            UPDATE gastos_mensais SET valor_total = ?, registrado_em = datetime('now', 'localtime')
                WHERE mes = ? AND ano = ?
                       """, (valor_total, mes, ano))
        conn.commit()
        conn.close()
        return "atualizado"
    
    cursor.execute("""
        INSERT INTO gastos_mensais (mes, ano, valor_total)
        VALUES(?, ?, ?)
    """, (mes, ano, valor_total))
    conn.commit()
    conn.close()
    return "inserido"
    
def buscar_gastos_mensais():
    #Retorna todos os gastos mensais ordenados por mes
    conn =conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT mes, ano, valor_total, registrado_em
        FROM gastos_mensais
        ORDER BY ano ASC, mes ASC
                   """)
    resultados = cursor.fetchall()
    conn.close()
    return resultados


def gasto_mes_registrado(mes, ano):
    #Verifica se ja existe registro no mês e ano selecionado
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT valor_total FROM gastos_mensais WHERE mes = ? AND ano = ?
    """, (mes, ano))
    resultado = cursor.fetchone()
    conn.close()
    return resultado[0] if resultado else None