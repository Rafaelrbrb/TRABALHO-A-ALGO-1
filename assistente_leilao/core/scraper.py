from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re


def extrair_numero(texto):
    try:
        numero = re.sub(r"[^\d,]", "", texto) #remove tudo que não é número ou vírgula
        numero = numero.replace(".", "")      # reove separador de milhar
        numero = numero.replace(",", ".")     # troca vírgula por ponto
        return float(numero)
    except Exception as e:
        print(f"Erro ao converter número: {e}")
        return None


def encontrar_por_xpath(driver, xpath):
    try:
        # 1. Encontrar o elemento
        elemento = driver.find_element(By.XPATH, xpath)
        
        # 2. Pegar o texto
        texto = elemento.text
        
        # 3. Limpar o preço (ex: "R$ 1.250,00" -> 1250.0)
        numero = extrair_numero(texto)
        
        return numero
    
    except Exception as e:
        print(f"Erro ao encontrar preço: {e}")
        return None
    

def encontrar_por_regex(driver, padrao):
    try:
        # 1. Pegar o HTML completo da página
        html = driver.find_element(By.TAG_NAME, "body").text
        
        # 2. Procurar o padrão (regex)
        match = re.search(padrao, html)
        
        if not match:
            return None
        
        # 3. Pegar o valor encontrado
        texto = match.group()
        
        # 4. Limpar o preço (ex: "R$ 1.250,00" -> 1250.0)
        texto = extrair_numero(texto)
        
        return texto
    
    except Exception as e:
        print(f"Erro ao encontrar preço com regex: {e}")
        return None
    