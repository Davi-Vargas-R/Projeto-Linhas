import pandas as pd

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
