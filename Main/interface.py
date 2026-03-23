from tkinter import Tk, filedialog

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

