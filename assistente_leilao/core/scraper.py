from __future__ import annotations

import logging
import re

from assistente_leilao.automation.page_finder import encontrar_valor

LOGGER = logging.getLogger(__name__)


def extrair_numero(texto: str) -> float | None:
    try:
        numero = re.sub(r"[^\d,.]", "", texto)
        if not numero:
            raise ValueError("nenhum número encontrado")

        if "," in numero and "." in numero:
            decimal = "," if numero.rfind(",") > numero.rfind(".") else "."
            milhar = "." if decimal == "," else ","
            numero = numero.replace(milhar, "")
            numero = numero.replace(decimal, ".")
        elif "," in numero:
            parte_inteira, parte_decimal = numero.rsplit(",", 1)
            if len(parte_decimal) in (1, 2):
                numero = f"{parte_inteira.replace(',', '')}.{parte_decimal}"
            else:
                numero = numero.replace(",", "")
        elif "." in numero:
            parte_inteira, parte_decimal = numero.rsplit(".", 1)
            if len(parte_decimal) in (1, 2):
                numero = f"{parte_inteira.replace('.', '')}.{parte_decimal}"
            else:
                numero = numero.replace(".", "")

        return float(numero)
    except Exception as e:
        LOGGER.warning("Erro ao converter número %r: %s", texto, e)
        return None


def obter_preco(driver, xpath: str = "", regex: str = "") -> float | None:
    texto = encontrar_valor(driver, xpath, regex)
    if texto is None:
        return None
    return extrair_numero(texto)
