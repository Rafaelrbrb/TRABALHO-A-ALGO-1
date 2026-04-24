from __future__ import annotations

import logging
import re
from functools import lru_cache

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOGGER = logging.getLogger(__name__)

WAIT_TIMEOUT = 2
WAIT_POLL_FREQUENCY = 0.2


@lru_cache(maxsize=32)
def _compilar_regex(regex: str):
    return re.compile(regex)


def _buscar_por_xpath(driver, xpath: str) -> str | None:
    try:
        wait = WebDriverWait(driver, WAIT_TIMEOUT, poll_frequency=WAIT_POLL_FREQUENCY)
        elemento = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        texto = elemento.text.strip()
        LOGGER.debug("Elemento encontrado via XPath: %s", xpath)
        return texto if texto else None
    except Exception:
        LOGGER.debug("XPath não encontrou elemento: %s", xpath)
        return None


def _buscar_por_regex(driver, regex: str) -> str | None:
    try:
        html = driver.page_source
        match = _compilar_regex(regex).search(html)
        if match:
            texto = match.group(0).strip()
            LOGGER.debug("Elemento encontrado via Regex: %s", regex)
            return texto
        LOGGER.debug("Regex não encontrou correspondência: %s", regex)
        return None
    except Exception:
        LOGGER.warning("Erro ao aplicar Regex: %s", regex)
        return None


def encontrar_valor(driver, xpath: str = "", regex: str = "") -> str | None:
    if xpath:
        resultado = _buscar_por_xpath(driver, xpath)
        if resultado is not None:
            return resultado

    if regex:
        resultado = _buscar_por_regex(driver, regex)
        if resultado is not None:
            return resultado

    LOGGER.debug("Nenhum seletor encontrou o elemento na página")
    return None
