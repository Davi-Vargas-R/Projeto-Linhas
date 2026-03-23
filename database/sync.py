from datetime import datetime
from database.conexao import conectar
from database.audit import registrar_auditoria

#Função para comparar dados no banco com os da planilha
def comparar_dados(df_banco, df_novo):
    chaves = ["id_usuario", "id_linha"]

    df_merge = df_banco.merge(
        df_novo,
        on=chaves,
        how="outer",
        suffixes=("_old", "_new"),
        indicator=True
    )

    adicionados = df_merge[df_merge["_merge"] == "right_only"]
    removidos = df_merge[df_merge["_merge"] == "left_only"]
    comuns = df_merge[df_merge["_merge"] == "both"]

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


#Função para atualizar os dados no banco utilizando também TRANSACTION
def sincronizar_banco(df_banco, df_novo):
    conn = conectar()
    cursor = conn.cursor()

    try:
        conn.execute("BEGIN")

        adicionados, removidos, alterados = comparar_dados(df_banco, df_novo)

        cursor.execute("""
        INSERT INTO importacoes (data_importacao, registros_processados)
        VALUES (?, ?)
        """, (datetime.now().isoformat(), len(df_novo)))

        id_importacao = cursor.lastrowid

        #ATIVAR / INSERIR
        for _, row in adicionados.iterrows():

            cursor.execute("""
            SELECT status_ativo FROM usuarios_linhas
            WHERE id_usuario = ? AND id_linha = ?
            """, (row["id_usuario"], row["id_linha"]))

            existente = cursor.fetchone()

            if existente:
                cursor.execute("""
                UPDATE usuarios_linhas
                SET status_ativo = 1,
                    valor_linha = ?,
                    status_linha = ?
                WHERE id_usuario = ? AND id_linha = ?
                """, (
                    row["valor_linha_new"],
                    row["status_linha_new"],
                    row["id_usuario"],
                    row["id_linha"]
                ))

                acao = "REATIVADO"
            else:
                cursor.execute("""
                INSERT INTO usuarios_linhas
                (id_usuario, id_linha, valor_linha, status_linha, status_ativo)
                VALUES (?, ?, ?, ?, 1)
                """, (
                    row["id_usuario"],
                    row["id_linha"],
                    row["valor_linha_new"],
                    row["status_linha_new"]
                ))

                acao = "INSERT"

            registrar_auditoria(
                cursor,
                acao,
                "usuarios_linhas",
                row,
                None,
                f'{row["valor_linha_new"]} | {row["status_linha_new"]}',
                id_importacao
            )

        #DESATIVAR (ANTES ERA DELETE)
        for _, row in removidos.iterrows():
            cursor.execute("""
            UPDATE usuarios_linhas
            SET status_ativo = 0
            WHERE id_usuario = ? AND id_linha = ?
            """, (
                row["id_usuario"],
                row["id_linha"]
            ))

            registrar_auditoria(
                cursor,
                "INATIVADO",
                "usuarios_linhas",
                row,
                f'{row["valor_linha_old"]} | {row["status_linha_old"]}',
                None,
                id_importacao
            )

        #ALTERAR
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

        conn.commit()
        print("Commit realizado com sucesso.")

    except Exception as e:
        conn.rollback()
        print("Erro! Rollback realizado.")
        print(e)

    finally:
        conn.close()

    print("Sincronização concluída. ")


