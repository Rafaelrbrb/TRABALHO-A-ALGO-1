import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WAIT_TIMEOUT = 10


def _buscar_por_xpath(driver, xpath: str) -> str | None:
    try:
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        elemento = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        texto = elemento.text.strip()
        print(f"[page_finder] Elemento encontrado via XPath: {xpath}")
        return texto if texto else None
    except Exception:
        print(f"[page_finder] XPath não encontrou elemento: {xpath}")
        return None


def _buscar_por_regex(driver, regex: str) -> str | None:
    try:
        html = driver.page_source
        match = re.search(regex, html)
        if match:
            texto = match.group(0).strip()
            print(f"[page_finder] Elemento encontrado via Regex: {regex}")
            return texto
        print(f"[page_finder] Regex não encontrou correspondência: {regex}")
        return None
    except Exception:
        print(f"[page_finder] Erro ao aplicar Regex: {regex}")
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

    print("[page_finder] Nenhum seletor encontrou o elemento na página.")
    return None