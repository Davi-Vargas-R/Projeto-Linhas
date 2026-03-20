import pandas as pd
from tkinter import Tk, filedialog
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment
from interface import escolher_planilha, escolher_onde_salvar
from processamento import mover_para_final, normalizar_msisdn 
from relatorio_excel import gerar_relatorio_excel
from database import criar_tabelas, inserir_linha, inserir_usuario, carregar_relacoes, comparar_dados, sincronizar_banco, obter_ou_criar_linha, obter_ou_criar_usuario
from datetime import datetime
import logging

logging.basicConfig(
    filename="execucao.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Script iniciado")

# Escolha das planilhas
caminho_planilha1 = escolher_planilha("Selecione a planilha Funcionários-Linhas(Dados)")
caminho_planilha2 = escolher_planilha("Selecione a planilha Base de dados Embratel(Linhas)")

# Leitura das planilhas
planilha1 = pd.read_excel(caminho_planilha1)
planilha2 = pd.read_excel(
    caminho_planilha2,
    sheet_name="Lista com Valores",
    dtype={'MSISDN': str}
)

#Defina quais colunas terão na planilha2
planilha2 = planilha2[['MSISDN', 'Status', 'Total Linha']]

# Renomear colunas
planilha2 = planilha2.rename(columns={
    'Total Linha': 'Valor',
    'Status': 'Status_Linha'
})


planilha1 = planilha1.rename(columns={
    'Setor_CNPJ': 'Setor'
})

# Normalizar nomes de colunas
planilha1.columns = planilha1.columns.str.strip().str.lower()
planilha2.columns = planilha2.columns.str.strip().str.lower()

# Normalizar msisdn
planilha1['msisdn'] = normalizar_msisdn(planilha1['msisdn'])
planilha2['msisdn'] = normalizar_msisdn(planilha2['msisdn'])

# Normalizar valores monetários
planilha2['valor'] = pd.to_numeric(
    planilha2['valor']
    .astype(str)
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False),
    errors='coerce'
)

# Merge das planilhas
planilhaTemp = pd.merge(planilha1, planilha2, on='msisdn', how='left')

# Colunas auxiliares
user = planilhaTemp['usuario']
status = planilhaTemp['status_atual']
linha = planilhaTemp['msisdn']

msisdn_vazio = linha.isna() | (linha.astype(str).str.strip() == '')

# Filtros
filtro_livre = (
    user.isna() |
    status.astype(str).str.strip().str.lower().isin(['demitido'])
)

filtro_ocupado = (
    user.notna() &
    ~user.astype(str).str.strip().str.lower().isin(['', 'não encontrado']) &
    ~status.astype(str).str.strip().str.lower().isin(['demitido']) &
    ~msisdn_vazio

) 

# Planilhas resultantes
linhas_livres = planilhaTemp[filtro_livre]
planilhaFinal = planilhaTemp[filtro_ocupado]

planilhaFinal = mover_para_final(planilhaFinal, 'valor')
linhas_livres = mover_para_final(linhas_livres, 'valor')

# Agrupamentos por setor
valor_total = planilhaTemp.groupby('setor', dropna=False)['valor'].sum()
valor_livre = linhas_livres.groupby('setor', dropna=False)['valor'].sum()
valor_ocupado = planilhaFinal.groupby('setor', dropna=False)['valor'].sum()

# Tabela resumo
valor_setor = pd.DataFrame({
    'setor': valor_total.index,
    'valor linhas livres': valor_livre.reindex(valor_total.index, fill_value=0).values,
    'valor linhas ocupadas': valor_ocupado.reindex(valor_total.index, fill_value=0).values,
    'valor total': valor_total.values,
})

print(planilhaFinal)

# Salvar arquivo
caminho_excel = escolher_onde_salvar(
    "Salvar relatório",
    "relatorio_final.xlsx"
)

base = caminho_excel.rsplit('.', 1)[0]

#aaaaaaaaaa

#Associando variavel para ter os valores da planilha final
planilhaDb=planilhaFinal.copy()

#Filtro de dados(se está vazio ou com espaços)
planilhaDb = planilhaDb[
    planilhaDb["msisdn"].notna() &
    planilhaDb["msisdn"].astype(str).str.strip().ne("") &
    planilhaDb["usuario"].notna() &
    planilhaDb["usuario"].astype(str).str.strip().ne("")
]

#Executar só diretamente
if __name__ == "__main__": 
    criar_tabelas() 
    ids_usuario = []
    ids_linha = []

    #Para indendependentes colunas na planilhaDb
    for _, row in planilhaDb.iterrows():

        #Confere se já possui aquele dado no banco, caso não, cria no banco e retorna o id recém criado 
        id_usuario = obter_ou_criar_usuario(row["usuario"])
        id_linha = obter_ou_criar_linha(row["msisdn"])

        #salva em 2 lista parelela
        ids_usuario.append(id_usuario)
        ids_linha.append(id_linha)

    #cria essas colunas na planilhaDb
    planilhaDb["id_usuario"] = ids_usuario
    planilhaDb["id_linha"] = ids_linha

    #remove duplicatas
    planilhaDb = planilhaDb.drop_duplicates(
        subset=["id_usuario", "id_linha"]
    )    
    
    #Cria novo Df selecionando só as colunas necessárias
    df_novo = planilhaDb[[ 
        "id_usuario", 
        "id_linha", 
        "valor", 
        "status_linha", 
        "usuario", 
        "msisdn" 
        ]].rename(columns={
            "valor": "valor_linha"
            }) 
    
    #Loop para inserir os dados(usuario e msisdn)
    for _, row in planilhaDb.iterrows(): 
        inserir_usuario(row["id_usuario"], row["usuario"]) 
        inserir_linha(row["id_linha"], row["msisdn"]) 

    #Pega estado atual do banco 
    df_banco = carregar_relacoes() 

    #compara banco com planilha
    adicionados, removidos, alterados = comparar_dados(df_banco, df_novo) 

    #Debug que mostra quantos registros mudaram
    print("Adicionados:", len(adicionados)) 
    print("Removidos:", len(removidos)) 
    print("Alterados:", len(alterados)) 

    #Sincroniza os dados no banco
    sincronizar_banco(df_banco, df_novo) 

#aaaaaaaaaa

gerar_relatorio_excel(caminho_excel, planilhaFinal, valor_setor)

# Exportar CSV
planilhaFinal.to_csv(
    base + ".csv",
    index=False,
    sep=";",
    encoding='utf-8-sig'
)

linhas_livres.to_csv(
    base + "_linhas_livres.csv",
    index=False,
    sep=";",
    encoding='utf-8-sig'
)
