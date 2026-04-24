# 💻 Assistente de Lances

Trabalho prático da disciplina de **Análise de Algoritmos**.

O projeto consiste em um sistema que monitora o preço de uma página web em tempo real e, ao detectar alterações, registra automaticamente o valor antigo e o novo em outra página pública.

---

## 👥 Integrantes

- Arthur  
- Davi  
- Leonardo  
- Matheus  
- Nikolas  
- Rafael  

---

## ⚙️ Requisitos

- Python **3.10 ou superior**
- Google Chrome instalado

---

## 🚀 Instalação

```bash
git clone <URL_DO_REPOSITORIO>
cd TRABALHO-A-ALGO-1
pip install -r requirements.txt
```

---

## ▶️ Como executar

```bash
cd assistente_leilao
python main.py
```

---

## 🧾 Entradas do sistema

Durante a execução, o sistema solicitará:

- **Nome** → mínimo de 3 letras (apenas letras)
- **URL** → página a ser monitorada
- **XPath** → caminho do elemento de preço (opcional)
- **Regex** → padrão alternativo para encontrar o preço (opcional)
- **Intervalo** → tempo em segundos entre cada verificação

---

## 🔍 Como descobrir o XPath

1. Abra a página no Chrome  
2. Clique com o botão direito no preço  
3. Clique em **Inspecionar**  
4. Clique com o botão direito no elemento destacado  
5. Vá em **Copy → Copy XPath**

---

## 💡 Exemplo de uso

Monitorando o preço do Bitcoin:

- URL: `https://finance.yahoo.com/quote/BTC-USD`
- XPath: `//*[@data-testid="qsp-price"]`
- Intervalo: `10`

---

## ⚙️ Funcionamento

1. O sistema acessa a página e captura o preço inicial  
2. A cada intervalo:
   - Recarrega a página  
   - Verifica se houve mudança  
3. Se o preço mudar:
   - Exibe o valor antigo e o novo no terminal  
   - Registra a mudança em log  
   - Acessa `https://demoqa.com/text-box`  
   - Preenche e envia automaticamente  
4. O monitoramento continua até `Ctrl + C`

---

## 🗂️ Estrutura do projeto

```bash
assistente_leilao/
├── core/
│   ├── scraper.py
│   ├── monitor.py
│   └── validator.py
├── automation/
│   ├── browser.py
│   ├── action.py
│   └── page_finder.py
├── interface/
│   └── cli.py
├── logs/
│   ├── activity_log.py
│   └── price_log.py
├── analysis/
│   └── complexity.py
├── tests/
└── main.py
```

---

## 📝 Logs

- As ações são registradas em `activity_log.txt`
- O arquivo é resetado a cada execução

---

## 📦 Dependências

- `selenium`  
- `webdriver-manager`  

---
