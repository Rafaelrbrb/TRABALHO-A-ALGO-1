import time
from interface.cli import coletar_configuracoes
from automation.browser import Browser
from automation.action import inserir_valores
from logs.activity_log import registrar_acao
from core.monitor import monitorar
from logs.activity_log import registrar_acao, limpar_log


if __name__ == "__main__":
    limpar_log()
    config = coletar_configuracoes()

    browser_monitor = Browser()
    browser_monitor.iniciar()
    browser_monitor.abrir_url(config["url"])
    time.sleep(5)  # aguarda carregar

    driver_monitor = browser_monitor.obter_driver()

    browser_acao = Browser()
    browser_acao.iniciar()
    browser_acao.abrir_url("https://demoqa.com/text-box")

    driver_acao = browser_acao.obter_driver()

    def callback(preco_antigo, preco_novo):
        registrar_acao(config["nome"], f"preço mudou de R${preco_antigo:.2f} para R${preco_novo:.2f}")
        inserir_valores(driver_acao, preco_antigo, preco_novo)

    try:
        monitorar(
            driver=driver_monitor,
            xpath=config["xpath"],
            regex=config["regex"],
            timeout=config["timeout"],
            callback=callback
        )
    finally:
        browser_monitor.fechar()
        browser_acao.fechar()