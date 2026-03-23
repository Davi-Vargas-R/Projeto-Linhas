📊 Projeto Linhas Telefônicas

Sistema desenvolvido em Python para análise, consolidação e sincronização de linhas telefônicas corporativas, com integração entre planilhas Excel, banco de dados SQLite e futura integração com API da operadora.

O projeto automatiza o tratamento de dados, identifica inconsistências, calcula custos por setor e mantém um histórico completo de alterações.

🚀 Funcionalidades

Importação de planilha interna (Funcionários x Linhas)

Integração com base da operadora (Excel ou API)

Normalização de números MSISDN

Consolidação de dados entre múltiplas fontes

Identificação de:

linhas ocupadas

linhas livres

Cálculo de custos por setor

Geração automática de:

relatório Excel

arquivos CSV

Sincronização com banco de dados SQLite

Registro de auditoria (INSERT, UPDATE, DELETE)

Registro de execução em log

Estrutura preparada para integração com API da Claro

🧱 Arquitetura do Sistema

O sistema segue um fluxo de ETL + sincronização de banco:

Entrada (Planilha/API)
        ↓
Tratamento e Normalização
        ↓
Consolidação (merge por MSISDN)
        ↓
Comparação com banco (snapshot)
        ↓
Sincronização (INSERT / UPDATE / DELETE)
        ↓
Auditoria + Relatórios
🗂 Estrutura do Projeto
Projeto-Linhas
│
├── main.py                # Orquestração do sistema
├── processamento.py       # Tratamento e limpeza de dados
├── interface.py           # Seleção de arquivos
├── relatorio_excel.py     # Geração de relatórios
├── database.py            # Banco SQLite + sincronização
├── integracao_claro.py    # Integração com API (em evolução)
│
├── execucao.log           # Log de execução (não versionado)
├── linhas.db              # Banco SQLite (não versionado)
│
├── README.md
└── .gitignore
⚙️ Tecnologias Utilizadas

Python 3

pandas

openpyxl

sqlite3

tkinter

requests (para integração com API)

📥 Entrada de Dados

O sistema utiliza duas fontes principais:

🧾 1. Planilha Interna (Funcionários x Linhas)

Contém:

usuário

msisdn

status do funcionário

setor

👉 Define quem usa cada linha

🌐 2. Base da Operadora

Pode vir de:

Excel (atual)

API (em implementação)

Contém:

MSISDN

status da linha

valor da linha

👉 Define custo e estado da linha

🔄 Fluxo de Processamento

Usuário seleciona a planilha interna

Sistema carrega base da operadora (Excel ou API)

Dados são normalizados

Merge entre bases pelo MSISDN

Classificação:

linhas ocupadas

linhas livres

Cálculo de valores por setor

Geração de relatórios

Comparação com estado atual do banco

Sincronização das diferenças

Registro em auditoria

📊 Saídas Geradas

O sistema gera automaticamente:

relatorio_final.xlsx

relatorio_final.csv

relatorio_final_linhas_livres.csv

🗄 Banco de Dados

Utiliza SQLite com estrutura normalizada:

Tabelas principais:

usuarios

linhas

usuarios_linhas (tabela relacional)

auditoria

importacoes

🔍 Auditoria

O sistema registra:

INSERT

UPDATE

DELETE

Com informações como:

usuário

msisdn

valores antigos e novos

data da alteração

🧾 Logs

Execuções registradas em:

execucao.log
▶️ Como Executar

Clone o repositório:

git clone https://github.com/Davi-Vargas-R/Projeto-Linhas.git

Instale as dependências:

pip install pandas openpyxl requests

Execute:

python main.py
📦 Gerar Executável

O projeto pode ser convertido em executável usando PyInstaller:

pyinstaller --onedir main.py

O executável será gerado em:

dist/main/
📈 Roadmap (Próximas Melhorias)

Integração completa com API da operadora

Detecção inteligente de troca de usuário (evitar DELETE + INSERT)

Otimização de performance (remoção de .iterrows())

Interface gráfica mais avançada

Automação (execução agendada)

Dashboard analítico (Power BI)

👨‍💻 Autor

Desenvolvido por Davi Vargas Ramalho