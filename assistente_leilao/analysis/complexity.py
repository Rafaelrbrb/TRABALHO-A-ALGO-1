# Análise de complexidade Big O
# Assistente de Lances


# scraper.py
# encontrar_por_xpath: O(1)
#   o selenium acha o elemento diretamente pelo xpath, nao depende do tamanho da pagina

# encontrar_por_regex: O(n)
#   onde n = tamanho do texto da pagina
#   o re.search percorre o texto inteiro ate achar o padrao

# extrair_numero: O(1)
#   opera sobre uma string pequena e fixa (o preco)


# monitor.py
# monitorar: O(t * n)
#   onde t = numero de iteracoes do loop
#   e n = tamanho do texto da pagina (vem do scraper)
#   cada iteracao chama o scraper que é O(n)


# validator.py
# validar_url: O(u) onde u = tamanho da url (na pratica O(1))
# validar_timeout: O(1)
# validar_nome_usuario: O(m) onde m = tamanho do nome (na pratica O(1))
# validar_tudo: O(1) na pratica


# logger/price_log.py
# registrar_mudanca: O(1)
#   so faz print e append na lista

# obter_historico: O(a)
#   onde a = numero de mudancas registradas
#   copia a lista inteira para retornar


# resumo geral
# +------------------------+----------+
# | funcao                 | Big O    |
# +------------------------+----------+
# | encontrar_por_xpath    | O(1)     |
# | encontrar_por_regex    | O(n)     |
# | extrair_numero         | O(1)     |
# | monitorar              | O(t * n) |
# | validar_tudo           | O(1)     |
# | registrar_mudanca      | O(1)     |
# | obter_historico        | O(a)     |
# +------------------------+----------+