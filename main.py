import pandas as pd
import logging
from services.pipeline import executar_pipeline

#Configura o log(registra as execuções)
logging.basicConfig(
    filename="execucao.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Script iniciado")

if __name__ == "__main__":
    executar_pipeline()