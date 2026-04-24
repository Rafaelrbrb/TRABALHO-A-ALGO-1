import logging
from datetime import datetime

LOG_FILE = "activity_log.txt"
LOGGER = logging.getLogger(__name__)

def registrar_acao(nome_usuario: str, acao: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{timestamp}] {nome_usuario}: {acao}\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(linha)
    
    LOGGER.info(linha.rstrip())


def obter_nome_usuario() -> str:
    while True:
        nome = input("Digite seu nome para registro de atividades: ").strip()
        if len(nome) >= 3 and nome.isalpha():
            registrar_acao(nome, "sessão iniciada")
            return nome
        print("Nome inválido: deve ter ao menos 3 letras e conter apenas letras.")

def limpar_log() -> None:
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("")
