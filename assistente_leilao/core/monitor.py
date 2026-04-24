from __future__ import annotations

import logging
import time

from assistente_leilao.core.scraper import obter_preco
from assistente_leilao.logs.price_log import registrar_mudanca

LOGGER = logging.getLogger(__name__)


def _notificar_status(status_callback, mensagem: str) -> None:
    if status_callback is not None:
        status_callback(mensagem)


def monitorar(driver, xpath, regex, timeout, callback=None, stop_event=None, status_callback=None):
    LOGGER.info("Iniciando monitoramento")

    preco_atual = obter_preco(driver, xpath, regex)

    if preco_atual is None:
        mensagem = "Não foi possível encontrar o preço inicial. Encerrando."
        LOGGER.warning(mensagem)
        _notificar_status(status_callback, mensagem)
        return

    LOGGER.info("Preço inicial: R$ %.2f", preco_atual)

    while stop_event is None or not stop_event.is_set():
        try:
            if stop_event is not None:
                if stop_event.wait(timeout):
                    break
            else:
                time.sleep(timeout)

            if stop_event is not None and stop_event.is_set():
                break

            driver.refresh()

            novo_preco = obter_preco(driver, xpath, regex)

            if novo_preco is None:
                mensagem = "Não foi possível ler o preço, tentando novamente..."
                LOGGER.warning(mensagem)
                _notificar_status(status_callback, mensagem)
                continue

            if novo_preco != preco_atual:
                registrar_mudanca(preco_atual, novo_preco)
                if callback:
                    callback(preco_antigo=preco_atual, preco_novo=novo_preco)
                preco_atual = novo_preco
            else:
                LOGGER.debug("Sem mudança. Preço atual: R$ %.2f", preco_atual)

        except KeyboardInterrupt:
            mensagem = "Monitoramento encerrado pelo usuário."
            LOGGER.info(mensagem)
            _notificar_status(status_callback, mensagem)
            break
        except Exception as e:
            mensagem = f"Erro durante o monitoramento: {e}"
            LOGGER.exception("Erro durante o monitoramento")
            _notificar_status(status_callback, mensagem)
            break

    if stop_event is not None and stop_event.is_set():
        mensagem = "Monitoramento encerrado pelo usuário."
        LOGGER.info(mensagem)
        _notificar_status(status_callback, mensagem)
