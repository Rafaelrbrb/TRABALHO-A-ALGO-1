import logging
from datetime import datetime

LOGGER = logging.getLogger(__name__)


def registrar_mudanca(preco_antigo, preco_novo):
    agora = datetime.now().strftime("%H:%M:%S")
    variacao = preco_novo - preco_antigo

    LOGGER.info(
        "[%s] preco mudou! antes=R$ %.2f agora=R$ %.2f variacao=R$ %.2f",
        agora,
        preco_antigo,
        preco_novo,
        variacao,
    )
