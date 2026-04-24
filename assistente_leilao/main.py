from interface.cli import coletar_configuracoes
from automation.browser import Browser
from automation.action import inserir_valores
from logs.activity_log import registrar_acao
from core.monitor import monitorar


if __name__ == "__main__":
    config = coletar_configuracoes()

    browser = Browser()
    browser.iniciar()
    browser.abrir_url(config["url"])
    driver = browser.obter_driver()

    def callback(preco_antigo, preco_novo):
        registrar_acao(config["nome"], f"preço mudou de R${preco_antigo:.2f} para R${preco_novo:.2f}")
        inserir_valores(driver, preco_antigo, preco_novo, url_origem=config["url"])

    try:
        monitorar(
            driver=driver,
            xpath=config["xpath"],
            regex=config["regex"],
            timeout=config["timeout"],
            callback=callback
        )
    finally:
        browser.fechar()