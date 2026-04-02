from tkinter import Tk, filedialog, messagebox, simpledialog
from datetime import datetime
from database.repositorio import registrar_gasto_mensal, gasto_mes_registrado

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


MESES_PT = {
    1: "Janeiro", 2:"Fevereiro", 3:"Março", 4:"Abril", 5:"Maio", 6:"Junho", 7:"Julho", 8:"Agosto", 9:"Setembro", 10:"Outubro", 11:"Novembro", 12:"Dezembro"
}

def gasto_mensal_interface(valor_total):
    #Abre uma janela de confirmação para o usuário registrar o gasto mensal e exibe um aviso caso o mês já tenha registro.
    root = Tk()
    root.withdraw()

    hoje = datetime.now()
    mes_num = hoje.month
    ano = hoje.year
    mes_nome = MESES_PT[mes_num]
    mes_str = str(mes_num).zfill(2)

    valor_formatado = f"R${valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    #Verifica se o mes já foi registrado

    valor_existente = gasto_mes_registrado(mes_str, ano)

    if valor_existente is not None:
        valor_existente_formatado = f"R${valor_existente:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        resposta = messagebox.askyesno(
            "Mês já registrado",
            f"O mês {mes_nome}/{ano} já possui um gasto registrado:\n\n"
            f"Valor atual: {valor_existente_formatado}\n"
            f"Novo valor: {valor_formatado}\n\n"
            f"Deseja substituir o valor registrado?"
        )
    else:
        resposta = messagebox.askyesno(
            "Registrar Gasto Mensal",
            f"Deseja registrar o seguinte gasto?\n\n"
            f"Mês: {mes_nome}/{ano}\n"
            f"Valor: {valor_formatado}"
        )

    root.destroy()

    if not resposta:
        return None
    
    status = registrar_gasto_mensal(mes_str, ano , valor_total)

    #Feedback do usuario

    root2 = Tk()
    root2.withdraw()
    if status =="inserido":
        messagebox.showinfo("Sucesso", f"Gasto de {mes_nome}/{ano} registrado com sucesso!\nValor: {valor_formatado}")

    elif status == "atualizado":
        messagebox.showinfo("Atualizado", f"Gasto de {mes_nome}/{ano} registrado com sucesso!\nValor: {valor_formatado}")

    elif status == "ignorado":
        messagebox.showinfo("Sem alteração", f"O valor já está registrado para {mes_nome}/{ano}.")
    root2.destroy()

    return status