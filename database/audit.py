from datetime import datetime
#Função responsável pela lógica da auditoria
def registrar_auditoria(cursor, acao, tabela, row, valor_antigo, valor_novo, id_importacao):
    data_atual = datetime.now().isoformat()

    if acao == "INSERT":
        data_criacao = data_atual
    else:
        data_criacao = None

    cursor.execute("""
    INSERT INTO auditoria (
        data, data_criacao, acao, tabela,
        id_usuario, id_linha,
        usuario, msisdn,
        valor_antigo, valor_novo,
        id_importacao
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data_atual,
        data_criacao,
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
   