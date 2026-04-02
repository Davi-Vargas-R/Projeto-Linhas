from datetime import datetime
from database.conexao import conectar

#Função que cria as tabelas caso não existam ainda(desse jeito para evitar de dar erro caso já exista)
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    #Tabela chave msisdn
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS linhas (
        id_linha INTEGER PRIMARY KEY,
        msisdn TEXT UNIQUE
    )               
    """)

    #Tabela chave usuario
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id_usuario INTEGER PRIMARY KEY,
        usuario TEXT UNIQUE
    )
    """)

    #Tabela pivô linha-usuario
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios_linhas (
        id_usuario INTEGER,
        id_linha INTEGER,
        valor_linha REAL,
        status_linha TEXT,
        status_ativo INTEGER DEFAULT 1,
        PRIMARY KEY (id_usuario, id_linha),
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
        FOREIGN KEY (id_linha) REFERENCES linhas(id_linha)
    )
    """)

    #Tabela de auditoria
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auditoria (
        id_log INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        data_criacao TEXT,
        acao TEXT,
        tabela TEXT,
        id_usuario INTEGER,
        id_linha INTEGER,
        usuario TEXT,
        msisdn TEXT,
        valor_antigo TEXT,
        valor_novo TEXT,
        id_importacao INTEGER
    )
    """)

    #Tabela para registrar importações
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS importacoes (
        id_importacao INTEGER PRIMARY KEY AUTOINCREMENT,
        data_importacao TEXT,
        registros_processados INTEGER
    )
    """)


    # Tabela de gastos mensais
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gastos_mensais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mes TEXT NOT NULL,
        ano INTEGER NOT NULL,
        valor_total REAL NOT NULL,
        registrado_em TEXT DEFAULT (datetime('now', 'localtime')),
        UNIQUE(mes, ano)
    )
    """)

    conn.commit()
    conn.close()
