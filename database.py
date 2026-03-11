import sqlite3
import pandas as pd
from datetime import datetime

def conectar():
    conn=sqlite3.connect("linhas.db")
    return conn

def criar_tabela():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS linhas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        msisdn TEXT,
        status_atual TEXT,
        setor TEXT,
        status_linha TEXT,
        valor REAL,
        data_execucao TEXT
)
""")
    
    conn.commit()
    conn.close()

def salvar_dataframe(df):

    conn =conectar()

    if "id" in df.columns:
        df = df.drop(columns=["id"])
    
    query = """
    SELECT l.*
    FROM linhas l
    INNER JOIN (
        SELECT msisdn, MAX(id) as max_id
        FROM linhas
        GROUP BY msisdn
    ) ult
    ON l.id = ult.max_id
    """
    try:
        df_banco = pd.read_sql(query, conn)
    except:
        df_banco = pd.DataFrame()

    if df_banco.empty:
        if "id" in df.columns:
            df = df.drop(columns=["id"])
        df["data_execucao"]=datetime.now()

        df.to_sql(
            "linhas",
            conn,
            if_exists="append",
            index=False
        )
        print("primeira carga de dados realizada")
        conn.close()
        return

    df_merge= df.merge(
        df_banco,
        on="msisdn",
        how="left",
        suffixes=("", "_old")
    )

    df_merge = df_merge.fillna("")

    colunas_comparar = [
        "usuario",
        "status_atual",
        "setor",
        "status_linha",
        "valor"
    ]

    mudancas=[]

    for col in colunas_comparar:
        mudancas.append(df_merge[col] != df_merge[f"{col}_old"])

    df_merge["mudou"] = pd.concat(mudancas, axis=1).any(axis=1)

    df_final =df_merge[df_merge["mudou"]== True]
    
    if not df_final.empty:

        df_final = df_final[df.columns]

        if "id" in df_final.columns:
            df_final = df_final.drop(columns=["id"])

        df_final['data_execucao'] = datetime.now()

        print(df_merge[df_merge["mudou"] == True][
        ["msisdn", "usuario", "usuario_old", "status_linha", "status_linha_old", "valor", "valor_old"]
         ])
        
        df_final.to_sql(
            "linhas",
            conn,
            if_exists="append",
            index=False
        )

        print(f"{len(df_final)} alterações salvas no histórico")

    else:
        print("Nenhuma alteração detectada")
    
    conn.close()

    
