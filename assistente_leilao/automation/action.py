from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

ACTION_URL = "https://httpbin.org/forms/post"
FIELD_SELECTOR = (By.NAME, "custname")
BUTTON_SELECTOR = (By.CSS_SELECTOR, "form button[type='submit']")
WAIT_TIMEOUT = 10


def inserir_valores(driver, valor_antigo, valor_novo) -> None:
    driver.get(ACTION_URL)

    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    campo = wait.until(EC.presence_of_element_located(FIELD_SELECTOR))
    campo.clear()
    campo.send_keys(f"Valor antigo: {valor_antigo} | Valor novo: {valor_novo}")

    botao = wait.until(EC.element_to_be_clickable(BUTTON_SELECTOR))
    botao.click()