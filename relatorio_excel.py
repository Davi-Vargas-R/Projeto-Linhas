import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment

def gerar_relatorio_excel(caminho_excel, planilhaFinal, valor_setor):

    with pd.ExcelWriter(caminho_excel) as writer:
        planilhaFinal.to_excel(writer, sheet_name='Usuários Válidos', index=False)
        valor_setor.to_excel(writer, sheet_name='Valor-Setor', index=False)

    # Estilização Excel
    wb = load_workbook(caminho_excel)

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

    wb.save(caminho_excel)