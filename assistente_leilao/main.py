from interface.cli import coletar_configuracoes
from automation.browser import Browser
from core.monitor import monitorar

if __name__ == "__main__":
    config = coletar_configuracoes()

    browser = Browser()
    browser.iniciar()
    browser.abrir_url(config["url"])
    driver = browser.obter_driver()

    monitorar(
        driver=driver,
        xpath=config["xpath"],
        regex=config["regex"],
        timeout=config["timeout"]
    )