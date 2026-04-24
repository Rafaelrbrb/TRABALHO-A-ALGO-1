from core.validator import validar_url, validar_timeout, validar_nome, validar_seletor
from logs.activity_log import registrar_acao


def pedir_nome() -> str:
    while True:
        nome = input("Digite seu nome (apenas letras, mínimo 3): ").strip()
        from core.validator import validar_nome
        erro = validar_nome(nome)
        if erro is None:
            registrar_acao(nome, "sessão iniciada")
            return nome
        print(f"  Erro: {erro}\n")


def pedir_url(nome: str) -> str:
    while True:
        url = input("Digite a URL para monitorar: ").strip()
        erro = validar_url(url)
        if erro is None:
            registrar_acao(nome, f"URL informada: {url}")
            return url
        print(f"  Erro: {erro}\n")


def pedir_timeout(nome: str) -> int:
    while True:
        timeout = input("Digite o intervalo de monitoramento em segundos (ex: 30): ").strip()
        erro = validar_timeout(timeout)
        if erro is None:
            registrar_acao(nome, f"Timeout informado: {timeout}s")
            return int(timeout)
        print(f"  Erro: {erro}\n")


def pedir_seletor(nome: str) -> tuple[str, str]:
    while True:
        xpath = input("Digite o XPath do campo (ou deixe vazio): ").strip()
        regex = input("Digite o Regex do campo (ou deixe vazio): ").strip()
        erro = validar_seletor(xpath, regex)
        if erro is None:
            registrar_acao(nome, f"Seletor informado — XPath: '{xpath}' | Regex: '{regex}'")
            return xpath, regex
        print(f"  Erro: {erro}\n")


def coletar_configuracoes() -> dict:
    print("\n=== ASSISTENTE DE LANCES ===\n")

    nome = pedir_nome()
    print(f"\n  Olá, {nome}!\n")

    url = pedir_url(nome)
    timeout = pedir_timeout(nome)
    xpath, regex = pedir_seletor(nome)

    config = {
        "nome": nome,
        "url": url,
        "timeout": timeout,
        "xpath": xpath,
        "regex": regex,
    }

    print("\n  Configurações aceitas! Iniciando monitoramento...\n")
    registrar_acao(nome, "monitoramento iniciado")
    return config