from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FIELD_SELECTOR = (By.ID, "userName")
BUTTON_SELECTOR = (By.ID, "submit")
WAIT_TIMEOUT = 10


def inserir_valores(driver, valor_antigo, valor_novo) -> None:
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    driver.execute_script("window.scrollTo(0, 0);")

    campo = wait.until(EC.element_to_be_clickable(FIELD_SELECTOR))
    campo.clear()
    campo.send_keys(f"Valor antigo: {valor_antigo} | Valor novo: {valor_novo}")

    botao = wait.until(EC.presence_of_element_located(BUTTON_SELECTOR))
    driver.execute_script("arguments[0].scrollIntoView();", botao)
    botao.click()