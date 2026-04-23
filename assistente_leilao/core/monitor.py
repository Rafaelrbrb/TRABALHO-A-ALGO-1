import time
from core import scraper


def monitorar(driver, xpath, regex, timeout, callback=None):

    print("iniciando monitoramento...")

    # pega o preço inicial
    preco_atual = scraper.encontrar_por_xpath(driver, xpath)
    if preco_atual is None:
        preco_atual = scraper.encontrar_por_regex(driver, regex)

    if preco_atual is None:
        print("nao consegui achar o preco, encerrando")
        return

    print("preco inicial:", preco_atual)

    while True:
        try:
            time.sleep(timeout)
            driver.refresh()

            novo_preco = scraper.encontrar_por_xpath(driver, xpath)
            if novo_preco is None:
                novo_preco = scraper.encontrar_por_regex(driver, regex)

            if novo_preco is None:
                print("nao consegui ler o preco, tentando de novo...")
                continue

            if novo_preco != preco_atual:
                print("preco mudou!", preco_atual, "->", novo_preco)
                if callback:
                    callback(preco_antigo=preco_atual, preco_novo=novo_preco)
                preco_atual = novo_preco
            else:
                print("sem mudanca, preco atual:", preco_atual)

        except KeyboardInterrupt:
            print("monitoramento encerrado")
            break