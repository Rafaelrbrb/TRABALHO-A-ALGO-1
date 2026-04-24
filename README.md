```markdown
# Assistente de Lances

Trabalho prático da disciplina de Análise de Algoritmos.

Sistema que monitora o preço de uma página web em tempo real e, ao detectar mudanças, registra automaticamente o valor antigo e o novo em outra página pública.

---

## Integrantes

- Arthur
- Davi
- Leonardo
- Matheus
- Nikolas
- Rafael

---

## Requisitos

- Python 3.10 ou superior
- Google Chrome instalado

---

## Instalação

1. Clone o repositório:
```
git clone <url-do-repositorio>
cd TRABALHO-A-ALGO-1
```

2. Instale as dependências:
```
pip install -r requirements.txt
```

---

## Como executar

Entre na pasta do projeto e rode:
```
cd assistente_leilao
python main.py
```

O sistema vai pedir as seguintes informações no terminal:

- **Nome** — seu nome (mínimo 3 letras, apenas letras)
- **URL** — endereço da página a ser monitorada
- **XPath** — caminho do campo de preço na página (ou deixe vazio)
- **Regex** — padrão para encontrar o preço (ou deixe vazio)
- **Intervalo** — tempo em segundos entre cada verificação

---

## Como descobrir o XPath de um elemento

1. Abre a página no Chrome
2. Clica com o botão direito no preço
3. Clica em **Inspecionar**
4. Clica com o botão direito no elemento destacado
5. **Copy → Copy XPath**

---

## Exemplo de uso

Para monitorar o preço do Bitcoin:

- URL: `https://finance.yahoo.com/quote/BTC-USD`
- XPath: `//*[@data-testid="qsp-price"]`
- Intervalo: `10`

---

## Funcionamento

1. O sistema abre a página informada e lê o preço inicial
2. A cada intervalo definido, recarrega a página e verifica se o preço mudou
3. Quando detecta uma mudança:
   - Exibe no terminal o valor antigo e o novo
   - Registra a ação no arquivo de log
   - Acessa a página `https://demoqa.com/text-box` em um segundo browser
   - Insere o texto com os dois valores e clica em Submit
4. Continua monitorando até o usuário encerrar com `Ctrl+C`

---

## Estrutura do projeto

```
assistente_leilao/
├── core/
│   ├── scraper.py       # localiza e extrai o preço da página
│   ├── monitor.py       # loop de monitoramento
│   └── validator.py     # validação das entradas do usuário
├── automation/
│   ├── browser.py       # gerencia o Chrome via Selenium
│   ├── action.py        # interage com a página alvo
│   └── page_finder.py   # busca o campo por XPath ou Regex
├── interface/
│   └── cli.py           # interface de linha de comando
├── logs/
│   ├── activity_log.py  # registra ações do usuário
│   └── price_log.py     # registra mudanças de preço
├── analysis/
│   └── complexity.py    # análise de complexidade Big O
├── tests/               # testes unitários
└── main.py              # ponto de entrada
```

---

## Logs

Todas as ações são salvas em `activity_log.txt` na raiz do projeto. O arquivo é resetado automaticamente a cada nova execução.

---

## Dependências

- `selenium` — automação do browser
- `webdriver-manager` — gerencia o ChromeDriver automaticamente
```
