from datetime import datetime


def registrar_mudanca(preco_antigo, preco_novo):

    agora = datetime.now().strftime("%H:%M:%S")
    variacao = preco_novo - preco_antigo

    print(f"[{agora}] preco mudou!")
    print(f"  antes: R$ {preco_antigo:.2f}")
    print(f"  agora: R$ {preco_novo:.2f}")
    print(f"  variacao: R$ {variacao:.2f}")