import re
from automation.page_finder import encontrar_valor


def extrair_numero(texto: str) -> float | None:
    try:
        numero = re.sub(r"[^\d,]", "", texto)  # remove tudo que não é número ou vírgula
        numero = numero.replace(".", "")        # remove separador de milhar
        numero = numero.replace(",", ".")       # troca vírgula por ponto
        return float(numero)
    except Exception as e:
        print(f"Erro ao converter número: {e}")
        return None


def obter_preco(driver, xpath: str = "", regex: str = "") -> float | None:
    texto = encontrar_valor(driver, xpath, regex)
    if texto is None:
        return None
    return extrair_numero(texto)