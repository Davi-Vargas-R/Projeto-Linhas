import pandas as pd
from tkinter import Tk, filedialog

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
#associa as planilhas a "variaveis" internas
planilha1 = escolher_planilha("Selecione a PRIMEIRA planilha (dados principais)")
planilha2 = escolher_planilha("Selecione a SEGUNDA planilha (linhas)")
#faz a junção das 2 planilhas, sendo que utiliza a coluna ID para tal, criando uma variavel temporaria
planilhaTemp = pd.merge(planilha1, planilha2, on='ID')

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

#Função criada para fins de organização(manda a coluna 'Valor' para ser a ultima )
def mover_para_final(df, coluna):
    cols = [c for c in df.columns if c != coluna] + [coluna]
    return df[cols]

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


#criação da planilha definitiva contendo os valores pagos mensalmente
with pd.ExcelWriter('C:/Users/davi.ramalho/Desktop/Estudos python/planilha_com_abas.xlsx') as writer:
    planilhaFinal.to_excel(writer, sheet_name='Usuários Válidos', index=False)
    valor_setor.to_excel(writer, sheet_name='Valor-Setor',index=False)
#criação das planilhas de saída nos arquivos do computador, pronto para serem abertas.
planilhaFinal.to_excel('C:/Users/davi.ramalho/Desktop/Estudos python/planilha_final.xlsx', index=False)
linhas_livres.to_excel('C:/Users/davi.ramalho/Desktop/Estudos python/linhas_livres.xlsx', index=False)
