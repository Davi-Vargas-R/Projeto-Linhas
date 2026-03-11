# 📊 Projeto Linhas Telefônicas

Sistema desenvolvido em **Python** para análise, organização e geração de relatórios de linhas telefônicas corporativas a partir de planilhas Excel.

O projeto automatiza a consolidação de dados de diferentes planilhas, identifica linhas ocupadas e livres, calcula valores por setor e mantém um **histórico de alterações em banco de dados SQLite**.

---

# 🚀 Funcionalidades

* Importação de planilhas Excel
* Normalização de números **MSISDN**
* Consolidação de dados de múltiplas bases
* Identificação de:

  * linhas ocupadas
  * linhas livres
* Cálculo de valores por **setor**
* Geração automática de **relatório Excel**
* Exportação de **CSV**
* Registro de alterações em **banco de dados SQLite**
* Registro de execução em **log**

---

# 🗂 Estrutura do Projeto

```
Projeto-Linhas
│
├── main.py                # Script principal
├── processamento.py       # Funções de tratamento de dados
├── interface.py           # Interface para seleção de arquivos
├── relatorio_excel.py     # Geração do relatório final
├── database.py            # Integração com banco SQLite
│
├── linhas.db              # Banco de dados gerado automaticamente
├── execucao.log           # Log de execuções
│
└── README.md
```

---

# ⚙️ Tecnologias Utilizadas

* Python 3
* pandas
* openpyxl
* sqlite3
* tkinter

---

# 📥 Entrada de Dados

O sistema utiliza duas planilhas principais:

### Planilha 1 — Funcionários / Linhas

Contém informações como:

* usuário
* msisdn
* status do funcionário
* setor

---

### Planilha 2 — Base de Linhas (Operadora)

Contém:

* MSISDN
* status da linha
* valor da linha

---

# 🔄 Fluxo de Processamento

1. Usuário seleciona as planilhas
2. O sistema normaliza os dados
3. Realiza o **merge das bases pelo MSISDN**
4. Classifica linhas em:

   * ocupadas
   * livres
5. Calcula valores por setor
6. Gera:

   * relatório Excel
   * arquivos CSV
7. Salva alterações detectadas no **SQLite**

---

# 📊 Saídas Geradas

O sistema gera automaticamente:

* `relatorio_final.xlsx`
* `relatorio_final.csv`
* `relatorio_final_linhas_livres.csv`

Além disso, registra alterações no banco:

```
linhas.db
```

---

# 🗄 Banco de Dados

O projeto utiliza **SQLite** para armazenar histórico das linhas processadas.

Tabela principal:

```
linhas
```

Campos:

* id
* usuario
* msisdn
* status_atual
* setor
* status_linha
* valor
* data_execucao

O sistema detecta alterações entre execuções e registra somente mudanças.

---

# 🧾 Logs

Todas as execuções são registradas em:

```
execucao.log
```

Isso permite rastrear execuções do script.

---

# ▶️ Como Executar

Clone o repositório:

```
git clone https://github.com/seu-usuario/projeto-linhas.git
```

Instale as dependências:

```
pip install pandas openpyxl
```

Execute o script:

```
python main.py
```

---

# 📈 Futuras Melhorias

* Dashboard com **Power BI**
* Melhor detecção de troca de usuários
* Estrutura de banco com histórico de vínculos
* Interface gráfica completa
* Automatização de execução

---

# 👨‍💻 Autor

Projeto desenvolvido por **Davi Vargas Ramalho**.
