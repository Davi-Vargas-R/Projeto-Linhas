import requests 
import pandas as pd

def autenticar_claro():
    url = "https://api.claro.com.br/oauth2/token"

    payload = {
        'grant_type': "client_credentials",
        'client_id': "CLIENTE ID AQUI (PLACEHOLDER)",
        'client_secret': "CLIENT SECRET AQUI (PLACEHOLDER)"
    }

    response = requests.post(url, data=payload)

    if response.status_code != 200:
        raise Exception("Erro ao autenticar na API da Claro")
    
    data = response.json()
    return data["access_token"]


def obter_dados_claro_api():
    dados_fake = [
        {"msisdn": "11999999999", "status_linha": "ATIVA", "valor": 50.0},
        {"msisdn": "11888888888", "status_linha": "CANCELADA", "valor": 30.0},
    ]

    return pd.DataFrame(dados_fake)