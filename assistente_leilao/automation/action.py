from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ACTION_URL = "https://httpbin.org/forms/post"
FIELD_SELECTOR = (By.NAME, "custname")
WAIT_TIMEOUT = 15


def inserir_valores(driver, valor_antigo, valor_novo, url_origem: str = "") -> None:
    driver.get(ACTION_URL)

    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # espera o campo de texto aparecer e insere os valores
    campo = wait.until(EC.presence_of_element_located(FIELD_SELECTOR))
    campo.clear()
    campo.send_keys(f"Valor antigo: {valor_antigo} | Valor novo: {valor_novo}")

    # tenta localizar o botão de submit por diferentes seletores
    for seletor in [
        (By.CSS_SELECTOR, "form button[type='submit']"),
        (By.CSS_SELECTOR, "input[type='submit']"),
        (By.XPATH, "//button[@type='submit']"),
        (By.XPATH, "//input[@type='submit']"),
        (By.XPATH, "//button[contains(text(),'Submit') or contains(text(),'submit')]"),
    ]:
        try:
            botao = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(seletor))
            botao.click()
            print(f"[action] Botão clicado com seletor: {seletor}")
            break
        except Exception:
            continue
    else:
        print("[action] AVISO: nenhum botão encontrado na página alvo.")

    # volta para a página do leilão para continuar monitorando
    if url_origem:
        driver.get(url_origem)
        print(f"[action] Voltando para: {url_origem}")