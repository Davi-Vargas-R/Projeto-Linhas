import pandas as pd
from tkinter import Tk, filedialog
from openpyxl import load_workbook

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

#Define user como a coluna Usuario, assim puxando todos os valores dessa coluna
user=planilhaTemp['Usuario']
status=planilhaTemp['status']
#Filtro para caso uma linha não possua dono, ou seja, está livre
filtro_livre=(
    user.isna()|
    user.astype(str).str.strip().str.lower().isin(['','não encontrado'])|
    status.astype(str).str.strip().str.lower().isin(['demitido'])
)

#Filtro para caso uma linha possua dono, ou seja, está ocupado
filtro_ocupado=(
    user.notna()&
    ~user.astype(str).str.strip().str.lower().isin(['','não encontrado'])&
    ~status.astype(str).str.strip().str.lower().isin(['demitido'])
)

#criação da planilha de linhas livres no sistema utilizando o filtro livre criado anteriormente 
linhas_livres= planilhaTemp[filtro_livre]

#criação da planilha planilhaFinal no sistema utilizando o filtro ocupado criado anteriormente 
planilhaFinal=planilhaTemp[filtro_ocupado]

planilhaFinal = mover_para_final(planilhaFinal, 'Valor')
linhas_livres = mover_para_final(linhas_livres, 'Valor')

#agrupamento dos valores baseado nos setores(quanto cada setor gasta com as linhas)
valor_total=planilhaTemp.groupby('Setor')['Valor'].sum()
valor_livre=linhas_livres.groupby('Setor')['Valor'].sum()
valor_ocupado=planilhaFinal.groupby('Setor')['Valor'].sum()

valor_setor=pd.DataFrame({
    'Setor': valor_total.index,
    'Valor Linhas Livres': valor_livre.reindex(valor_total.index, fill_value=0).values,
    'Valor Linhas Ocupadas': valor_ocupado.reindex(valor_total.index, fill_value=0).values,
    'Valor Total': valor_total.values,
    })
#Print no sistema para motivos de teste rápido
print(planilhaFinal)

caminho_excel=escolher_onde_salvar(
    "Salvar relatório",
    "relatório_final.xlsx"
)
base= caminho_excel.rsplit('.', 1)[0]
with pd.ExcelWriter(base+".xlsx") as writer:
    planilhaFinal.to_excel(writer, sheet_name='Usuários Válidos', index=False)
    valor_setor.to_excel(writer, sheet_name='Valor-Setor', index=False)

wb= load_workbook(base+".xlsx")
ws= wb['Usuários Válidos']

for cell in ws[1]:
    cell.font = cell.font.copy(bold=True)

wb.save(vase+'.xlsx')

planilhaFinal.to_csv(
    base+".csv",
    index=False,
    sep=";",
    encoding='utf-8-sig'
)
linhas_livres.to_csv(
    base+".csv",
    index=False,
    sep=";",
    encoding='utf-8-sig'
)

