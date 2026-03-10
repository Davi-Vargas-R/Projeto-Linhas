import pandas as pd
from tkinter import Tk, filedialog
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment


#Função para usuário escolher as planilhas salvas nos arquivos do próprio computador
def escolher_planilha(titulo):
    root = Tk()
    root.withdraw()
    caminho = filedialog.askopenfilename(
        title=titulo,
        filetypes=[("Arquivos Excel", "*.xlsx *.xls")]
    )
    if not caminho:
        raise Exception("Nenhum arquivo selecionado")
    return caminho


#Função para usuário escolher onde as planilhas serão salvas
def escolher_onde_salvar(titulo, nome):
    root = Tk()
    root.withdraw()
    caminho = filedialog.asksaveasfilename(
        title=titulo,
        defaultextension=".xlsx",
        initialfile=nome,
        filetypes=[("Arquivos Excel", "*.xlsx")]
    )
    if not caminho:
        raise Exception("Local para salvar não selecionado")
    return caminho

#Função para fins de organização da planilha(manda a coluna selecionada para ser a última)
def mover_para_final(df, coluna):
    cols = [c for c in df.columns if c != coluna] + [coluna]
    return df[cols]


#Função para normalizar o msisdn(retira o 55 caso possua)
def normalizar_msisdn(col):
    return (
        col.astype(str)
        .str.replace(r'^55', '', regex=True)
        .str.strip()
    )


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
    'Status': 'Status-Linha'
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

with pd.ExcelWriter(base + ".xlsx") as writer:
    planilhaFinal.to_excel(writer, sheet_name='Usuários Válidos', index=False)
    valor_setor.to_excel(writer, sheet_name='Valor-Setor', index=False)

# Estilização Excel
wb = load_workbook(base + ".xlsx")

header_fill = PatternFill(start_color="006633", end_color="006633", fill_type="solid")
linha_fill = PatternFill(start_color="E8F5E9", end_color="E8F5E9", fill_type="solid")

#Borda
borda = Border(
    left=Side(style='thin'),
    right=Side(style='thin'),
    top=Side(style='thin'),
    bottom=Side(style='thin')
)

for ws in wb.worksheets:

    ws.freeze_panes = "A2"
    
    #Cabeçalho
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = borda

    #Linhas zebra + bordas
    for row in ws.iter_rows(min_row=2):
        if row[0].row % 2==0:
            for cell in row:
                cell.fill = linha_fill

        for cell in row:
            cell.border = borda
            cell.alignment = Alignment(vertical="center")
            
    # Ajustar largura das colunas
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter

        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass

        ws.column_dimensions[col_letter].width = max_length + 2

    ws.auto_filter.ref = ws.dimensions

wb.save(base + '.xlsx')

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
