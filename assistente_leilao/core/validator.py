from __future__ import annotations

from urllib.parse import urlparse

def validar_url(url: str) -> str | None:
    parsed = urlparse(url.strip())

    if parsed.scheme not in ["http", "https"]:
        return "URL inválida: scheme deve ser http ou https"
    
    if not parsed.netloc:
        return "URL inválida: domínio (netloc) está vazio"
    
    return None


def validar_timeout(timeout) -> str | None:
    if isinstance(timeout, str):
        timeout = timeout.strip()

    try:
        valor = int(timeout)
    except (ValueError, TypeError):
        return "Timeout inválido: deve ser um número inteiro"

    if valor <= 0:
        return "Timeout inválido: deve ser maior que zero"

    return None


def validar_nome(nome: str) -> str | None:
    nome = nome.strip()

    if len(nome) < 3:
        return "Nome inválido: deve ter pelo menos 3 caracteres"

    if not nome.isalpha():
        return "Nome inválido: deve conter apenas letras"

    return None


def validar_seletor(xpath: str, regex: str) -> str | None:
    if not xpath and not regex:
        return "Seletor inválido: informe pelo menos xpath ou regex"

    return None


def validar_tudo(url, timeout, nome, xpath, regex) -> list[str]:
    erros = []

    erro = validar_url(url)
    if erro is not None:
        erros.append(erro)

    erro = validar_timeout(timeout)
    if erro is not None:
        erros.append(erro)

    erro = validar_nome(nome)
    if erro is not None:
        erros.append(erro)

    erro = validar_seletor(xpath, regex)
    if erro is not None:
        erros.append(erro)

    return erros
