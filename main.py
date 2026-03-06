import pandas as pd
from tkinter import Tk, filedialog
from openpyxl import load_workbook
<<<<<<< HEAD
from openpyxl.styles import PatternFill, Font
=======
>>>>>>> 607a944b5ab49e1f952617f2a7bd4350b9d13ecb

#Função para deixar o usuário escolher as planilhas
def escolher_planilha(titulo):
    root= Tk()
    root.withdraw() 
    caminho=filedialog.askopenfilename(
        title=titulo,
        filetypes=[("Arquivos Excel", "*.xlsx *.xls")]
    )
    if not caminho:
        raise Exception("Nenhum arquivo selecionado")
    return caminho
<<<<<<< HEAD
=======

def escolher_onde_salvar(titulo, nome):
    root= tk()
    root.withdraw
    caminho = filedialog.asksaveasfilename(
        title=titulo,
        defaultextension=".xlsx",
        initialfile="nome",
        filetypes=[("Arquivos Excel",'*.xlsx')]
    )
    if not caminho:
        raise Exception("Local para salvar não selecionado")
    return caminho

#Função criada para fins de organização(manda a coluna 'Valor' para ser a ultima )
def mover_para_final(df, coluna):
    cols = [c for c in df.columns if c != coluna] + [coluna]
    return df[cols]

#associa as planilhas a "variaveis" internas
planilha1 = escolher_planilha("Selecione a PRIMEIRA planilha (dados principais)")
planilha2 = escolher_planilha("Selecione a SEGUNDA planilha (linhas)")

#faz a junção das 2 planilhas, sendo que utiliza a coluna ID para tal, criando uma variavel temporaria
planilhaTemp = pd.merge(planilha1, planilha2, on='MSISDN')
>>>>>>> 607a944b5ab49e1f952617f2a7bd4350b9d13ecb

def escolher_onde_salvar(titulo, nome):
    root= Tk()
    root.withdraw()
    caminho = filedialog.asksaveasfilename(
        title=titulo,
        defaultextension=".xlsx",
        initialfile="nome",
        filetypes=[("Arquivos Excel",'*.xlsx')]
    )
    if not caminho:
        raise Exception("Local para salvar não selecionado")
    return caminho

#Função criada para fins de organização(manda a coluna 'Valor' para ser a ultima )
def mover_para_final(df, coluna):
    cols = [c for c in df.columns if c != coluna] + [coluna]
    return df[cols]

#Usuário escolhe as planilhas que serão utilizadas
caminho_planilha1 = escolher_planilha("Selecione a PRIMEIRA planilha (dados principais)")
caminho_planilha2 = escolher_planilha("Selecione a SEGUNDA planilha (linhas)")

#associa as planilhas a "variaveis" internas
planilha1 = pd.read_excel(caminho_planilha1)
planilha2 = pd.read_excel(caminho_planilha2, sheet_name="Lista com Valores")
planilha2 = planilha2[['MSISDN', 'Status', 'Total Linha']]

#Altera o nome de 2 colunas para fins de normalização
planilha2 = planilha2.rename(columns={
    'Total Linha': 'Valor'
})
planilha1 = planilha1.rename(columns={
    'Setor_CNPJ': 'Setor'
})

#Transforma as colunas em minuscula para fins de normalização de dados
planilha1.columns = planilha1.columns.str.strip().str.lower()
planilha2.columns = planilha2.columns.str.strip().str.lower()

#Transforma as colunas msisdn em str para não dar conflito
planilha1['msisdn'] = planilha1['msisdn'].astype(str)
planilha2['msisdn'] = planilha2['msisdn'].astype(str)

#Retira o "55" presente em alguns numeros
planilha1['msisdn'] = planilha1['msisdn'].str.replace(r'^55', '', regex=True)
planilha2['msisdn'] = planilha2['msisdn'].str.replace(r'^55', '', regex=True)

planilha2['valor'] = (
    planilha2['valor']
    .astype(str)
    .str.replace('.', '', regex=False)   # remove separador de milhar
    .str.replace(',', '.', regex=False)  # troca vírgula por ponto
)

#Transforma os valores da coluna "valor" de str para int
planilha2['valor'] = pd.to_numeric(planilha2['valor'], errors='coerce')
#faz a junção das 2 planilhas, sendo que utiliza a coluna ID para tal, criando uma variavel temporaria
planilhaTemp = pd.merge(planilha1, planilha2, on='msisdn', how='left')

#Define user como a coluna Usuario que será utilizada para puxar todos os valores dessa coluna
user=planilhaTemp['usuario']
status=planilhaTemp['status_atual']
linha=planilhaTemp['msisdn']

msisdn_vazio= linha.isna()| (linha.astype(str).str.strip()=='')
#Filtro para caso uma linha não possua dono, ou seja, está livre
filtro_livre=(
    user.isna()|
    status.astype(str).str.strip().str.lower().isin(['demitido'])
)

#Filtro para caso uma linha possua dono, ou seja, está ocupado
filtro_ocupado=(
    (
    user.notna()&
    ~user.astype(str).str.strip().str.lower().isin(['','não encontrado'])&
    ~status.astype(str).str.strip().str.lower().isin(['demitido'])
    |msisdn_vazio
    )
)


#criação da planilha de linhas livres no sistema utilizando o filtro livre criado anteriormente 
linhas_livres= planilhaTemp[filtro_livre]

#criação da planilha planilhaFinal no sistema utilizando o filtro ocupado criado anteriormente 
planilhaFinal=planilhaTemp[filtro_ocupado]

<<<<<<< HEAD
planilhaFinal = mover_para_final(planilhaFinal, 'valor')
linhas_livres = mover_para_final(linhas_livres, 'valor')
=======
planilhaFinal = mover_para_final(planilhaFinal, 'Valor')
linhas_livres = mover_para_final(linhas_livres, 'Valor')
>>>>>>> 607a944b5ab49e1f952617f2a7bd4350b9d13ecb

#agrupamento dos valores baseado nos setores(quanto cada setor gasta com as linhas)
valor_total=planilhaTemp.groupby('setor')['valor'].sum()
valor_livre=linhas_livres.groupby('setor')['valor'].sum()
valor_ocupado=planilhaFinal.groupby('setor')['valor'].sum()

#criação das colunas presentes na segunda aba da planilha final
valor_setor=pd.DataFrame({
    'setor': valor_total.index,
    'valor linhas livres': valor_livre.reindex(valor_total.index, fill_value=0).values,
    'valor linhas ocupadas': valor_ocupado.reindex(valor_total.index, fill_value=0).values,
    'valor total': valor_total.values,
    })
#Print no sistema para motivos de teste rápido
print(planilhaFinal)

<<<<<<< HEAD
#chama a função de salvar dados e envia os parametros
=======
>>>>>>> 607a944b5ab49e1f952617f2a7bd4350b9d13ecb
caminho_excel=escolher_onde_salvar(
    "Salvar relatório",
    "relatório_final.xlsx"
)
<<<<<<< HEAD
#cria a planilha final com as 2 abas
=======
>>>>>>> 607a944b5ab49e1f952617f2a7bd4350b9d13ecb
base= caminho_excel.rsplit('.', 1)[0]
with pd.ExcelWriter(base+".xlsx") as writer:
    planilhaFinal.to_excel(writer, sheet_name='Usuários Válidos', index=False)
    valor_setor.to_excel(writer, sheet_name='Valor-Setor', index=False)

wb= load_workbook(base+".xlsx")
ws= wb['Usuários Válidos']

<<<<<<< HEAD
#Estilo cabeçalho
ws.freeze_panes ="A2" #congela cabeçalho
header_fill= PatternFill(start_color="33FF33", end_color="33FF33", fill_type="solid")

for cell in ws[1]:
    cell.font= Font(bold=True, color="FFFFFF")
    cell.fill= header_fill

#Ajusta a largura das colunas
for col in ws.columns:
    max_length= 0
    col_letter= col[0].column_letter

    for cell in col:
        try:
            if cell.value:
                max_length=max(max_length, len(str(cell.value)))
        except:
            pass
    ws.column_dimensions[col_letter].width= max_length+2

ws.auto_filter.ref = ws.dimensions

wb.save(base+'.xlsx')

#cria o arquivo .csv da planilha final
=======
for cell in ws[1]:
    cell.font = cell.font.copy(bold=True)

wb.save(vase+'.xlsx')

>>>>>>> 607a944b5ab49e1f952617f2a7bd4350b9d13ecb
planilhaFinal.to_csv(
    base+".csv",
    index=False,
    sep=";",
    encoding='utf-8-sig'
)
<<<<<<< HEAD

#cria o arquivo .csv da planilha linhas livres
linhas_livres.to_csv(
    base+"linhas_livres.csv",
=======
linhas_livres.to_csv(
    base+".csv",
>>>>>>> 607a944b5ab49e1f952617f2a7bd4350b9d13ecb
    index=False,
    sep=";",
    encoding='utf-8-sig'
)
<<<<<<< HEAD
=======

>>>>>>> 607a944b5ab49e1f952617f2a7bd4350b9d13ecb
