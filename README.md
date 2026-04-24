# 🤖 Assistente de Lances para Leilão

Este projeto é um sistema de automação e monitoramento de preços em tempo real, desenvolvido para identificar variações em páginas web e realizar ações automáticas em sistemas externos.

## 👥 Identificação
- **Desenvolvedores:** Leonardo Lustosa
Rafael 
Davi
Matheus
Arthur
Nikolas
- **Status:** Funcional / Versão Final

## 📂 Estrutura do Projeto
```text
.
├── automation/
│   ├── action.py      # Interação com formulários externos (httpbin)
│   └── browser.py     # Configuração do Selenium (Modo Ninja)
├── core/
│   ├── monitor.py     # Loop de monitoramento e comparação
│   ├── scraper.py     # Extração e limpeza de dados (XPath/Regex)
│   └── validator.py   # Validação de entradas do usuário
├── interface/
│   └── gui.py         # Interface gráfica em Tkinter
├── logs/
│   ├── activity_log.txt # Histórico de ações do usuário
│   └── price_log.txt    # Histórico de variações de preço
├── main.py            # Ponto de entrada do sistema
└── test_scraper.py    # Testes unitários automatizados
🚀 Como ExecutarInstale as dependências: pip install selenium webdriver-managerExecute o arquivo principal: python main.pyPara rodar os testes: python test_scraper.py⚙️ Informações TécnicasAnálise de Complexidade (Big O)A localização da variável na página via XPath ou Regex possui uma complexidade de $O(N)$, onde $N$ é o número total de elementos (nós) no DOM da página. Isso ocorre porque o motor de busca do navegador precisa percorrer a árvore de elementos para encontrar o padrão correspondente.LogsActivity Log: Registra cada clique, erro e início de sessão do usuário.Price Log: Registra o valor antigo, o valor novo e a variação exata detectada.
---

### 2. Criar o arquivo de Testes (Para ganhar +1 ponto)
O professor pediu testes unitários. Crie um arquivo chamado **`test_scraper.py`** e cole isso:

```python
import unittest
from core.scraper import extrair_numero

class TestScraper(unittest.TestCase):
    def test_conversao_padrao_br(self):
        # Testa se converte 395.308,92 para 395308.92
        self.assertEqual(extrair_numero("395.308,92"), 395308.92)

    def test_limpeza_texto_sujo(self):
        # Testa se limpa símbolos de moeda e porcentagem
        self.assertEqual(extrair_numero("R$ 1.250,00 +0,15%"), 1250.00)

if __name__ == "__main__":
    unittest.main()