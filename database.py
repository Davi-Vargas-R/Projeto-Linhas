import sqlite3
import pandas as pd
from datetime import datetime


#Função só pra eu não ter que colocar esse trecho de definir conexão toda hora
def conectar():
    conn=sqlite3.connect("linhas.db")
    return conn

#Função que cria as tabelas caso não existam ainda(desse jeito evitar de dar erro caso já exista)
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS linhas (
        id_linha INTEGER PRIMARY KEY,
        msisdn TEXT UNIQUE
    )               
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id_usuario INTEGER PRIMARY KEY,
        usuario TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios_linhas (
        id_usuario INTEGER,
        id_linha INTEGER,
        valor_linha REAL,
        status_linha TEXT,
        PRIMARY KEY (id_usuario, id_linha),
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
        FOREIGN KEY (id_linha) REFERENCES linhas(id_linha)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auditoria (
        id_log INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS importacoes (
        id_importacao INTEGER PRIMARY KEY AUTOINCREMENT,
        data_importacao TEXT,
        registros_processados INTEGER
    )
    """)

    conn.commit()
    conn.close()

def inserir_usuario(id_usuario, usuario):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO usuarios (id_usuario, usuario)
    VALUES (?, ?)
    """, (id_usuario, usuario))

    conn.commit()
    conn.close()


def inserir_linha(id_linha, msisdn):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO linhas (id_linha, msisdn)
    VALUES (?, ?)
    """, (id_linha, msisdn))

    conn.commit()
    conn.close()


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
    """, conn)

    conn.close()
    return df

def comparar_dados(df_banco, df_novo):
    # chave composta
    chaves = ["id_usuario", "id_linha"]

    # merge completo
    df_merge = df_banco.merge(
        df_novo,
        on=chaves,
        how="outer",
        suffixes=("_old", "_new"),
        indicator=True
    )

    #adicionados (so no novo)
    adicionados =df_merge[df_merge["_merge"] == "right_only"]

    #removidos (so no banco)
    removidos = df_merge[df_merge["_merge"] == "left_only"]

    # possíveis atualizações (existem nos dois)
    comuns = df_merge[df_merge["_merge"] == "both"]

    # 🔥 tratar NaN como iguais
    cond_valor = (
        (comuns["valor_linha_old"] == comuns["valor_linha_new"]) |
        (comuns["valor_linha_old"].isna() & comuns["valor_linha_new"].isna())
    )

    cond_status = (
        (comuns["status_linha_old"] == comuns["status_linha_new"]) |
        (comuns["status_linha_old"].isna() & comuns["status_linha_new"].isna())
    )

    alterados = comuns[~(cond_valor & cond_status)]

    return adicionados, removidos, alterados


def registrar_auditoria(cursor, acao, tabela, row, valor_antigo, valor_novo, id_importacao):
    cursor.execute("""
    INSERT INTO auditoria (
        data, acao, tabela,
        id_usuario, id_linha,
        usuario, msisdn,
        valor_antigo, valor_novo,
        id_importacao
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        acao,
        tabela,
        row.get("id_usuario"),
        row.get("id_linha"),
        row.get("usuario"),
        row.get("msisdn"),
        str(valor_antigo),
        str(valor_novo),
        id_importacao
    ))

   

def sincronizar_banco(df_banco, df_novo):
    conn = conectar()
    cursor = conn.cursor()

    try:
        #INICIA TRANSAÇÃO
        conn.execute("BEGIN")

        adicionados, removidos, alterados = comparar_dados(df_banco, df_novo)

        cursor.execute("""
        INSERT INTO importacoes (data_importacao, registros_processados)
        VALUES (?, ?)
        """, (datetime.now().isoformat(), len(df_novo)))

        id_importacao = cursor.lastrowid

        for _, row in adicionados.iterrows():
            cursor.execute("""
            INSERT INTO usuarios_linhas
            (id_usuario, id_linha, valor_linha, status_linha)
            VALUES (?, ?, ?, ?)
            """, (
                row["id_usuario"],
                row["id_linha"],
                row["valor_linha_new"],
                row["status_linha_new"]
            ))

            registrar_auditoria(
                cursor,
                "INSERT",
                "usuarios_linhas",
                row,
                None,
                f'{row["valor_linha_new"]} | {row["status_linha_new"]}',
                id_importacao
            )

        for _, row in removidos.iterrows():
            cursor.execute("""
            DELETE FROM usuarios_linhas
            WHERE id_usuario = ? AND id_linha = ?
            """, (
                row["id_usuario"],
                row["id_linha"]
            ))

            registrar_auditoria(
                cursor,
                "DELETE",
                "usuarios_linhas",
                row,
                f'{row["valor_linha_old"]} | {row["status_linha_old"]}',
                None,
                id_importacao
            )

        for _, row in alterados.iterrows():
            cursor.execute("""
            UPDATE usuarios_linhas
            SET valor_linha = ?, status_linha = ?
            WHERE id_usuario = ? AND id_linha = ?
            """, (
                row["valor_linha_new"],
                row["status_linha_new"],
                row["id_usuario"],
                row["id_linha"]
            ))

            registrar_auditoria(
                cursor,
                "UPDATE",
                "usuarios_linhas",
                row,
                f'{row["valor_linha_old"]} | {row["status_linha_old"]}',
                f'{row["valor_linha_new"]} | {row["status_linha_new"]}',
                id_importacao
            )

        #SE TUDO DEU CERTO
        conn.commit()
        print("Commit realizado com sucesso.")

    except Exception as e:
        #SE DER ERRO
        conn.rollback()
        print("Erro! Rollback realizado.")
        print(e)

    finally:
        conn.close()

    print("Sincronização concluída. ")


def buscar_usuario_por_nome(usuario):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id_usuario FROM usuarios WHERE usuario = ?", (usuario,))
    resultado = cursor.fetchone()

    conn.close()
    return resultado[0] if resultado else None

def buscar_linha_por_msisdn(msisdn):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT id_linha FROM linhas WHERE msisdn = ?", (msisdn,))
    resultado = cursor.fetchone()

    conn.close()
    return resultado[0] if resultado else None

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

