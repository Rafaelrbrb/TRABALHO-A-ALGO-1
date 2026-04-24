import time
from core.scraper import obter_preco
from logs.price_log import registrar_mudanca


def monitorar(driver, xpath, regex, timeout, callback=None):
    print("Iniciando monitoramento...")

    preco_atual = obter_preco(driver, xpath, regex)

    if preco_atual is None:
        print("Não foi possível encontrar o preço inicial. Encerrando.")
        return


    print(f"Preço inicial: R$ {preco_atual:.4f}")

    while True:
        try:
            time.sleep(timeout)
            driver.refresh()

            novo_preco = obter_preco(driver, xpath, regex)

            if novo_preco is None:
                print("Não foi possível ler o preço, tentando novamente...")
                continue


            if novo_preco != preco_atual:
                registrar_mudanca(preco_atual, novo_preco)
                if callback:
                    callback(preco_antigo=preco_atual, preco_novo=novo_preco)
                preco_atual = novo_preco
            else:
                print(f"Sem mudança. Preço atual: R$ {preco_atual:.4f}")

        except KeyboardInterrupt:
            print("Monitoramento encerrado pelo usuário.")
            break