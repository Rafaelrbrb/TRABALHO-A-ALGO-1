# 🤖 Assistente de Lances para Leilão (Python Automation)

Este projeto consiste em um sistema inteligente de monitoramento de variáveis em páginas web de estrutura dinâmica. O software é capaz de identificar mudanças de preço em tempo real, calcular variações e interagir automaticamente com sistemas externos para registro de ocorrências.

---

## 👤 Identificação dos Alunos
| Nome | 
| :--- | 
| **Leonardo** |
| **Rafael** |
| **Davi** | 
| **Nikolas** |
| **Matheus** |
| **Arthur** |

**Projeto:** Sistema de Monitoramento e Assistente de Lances  
**Versão:** 1.0.0

---

## 🛠️ Arquitetura do Sistema
O projeto foi estruturado seguindo princípios de modularidade para facilitar a manutenção e garantir a estabilidade:

* **automation/**: Contém a lógica de interação com páginas externas (httpbin) e configuração do Selenium.
* **core/**: O "coração" do sistema, com o loop de monitoramento, extração de dados (scraper) e validadores.
* **interface/**: Gerenciamento da janela gráfica desenvolvida em Tkinter.
* **logs/**: Armazenamento dos arquivos `.txt` com o histórico de atividades e preços.
* **main.py**: Arquivo principal que inicia a aplicação.

---

## 📈 Análise de Complexidade (Big O)
Um dos requisitos fundamentais do projeto é a compreensão da eficiência do algoritmo utilizado:

* **Busca de Elementos:** A localização do preço via XPath ou Expressões Regulares (Regex) dentro do DOM (Document Object Model) possui complexidade de **O(N)**, onde **N** representa o número total de elementos no HTML da página.
* **Por que O(N)?** Para encontrar um elemento específico em uma estrutura de árvore de dados desconhecida, o navegador precisa realizar uma varredura que, no pior caso, visita todos os nós até localizar o alvo correspondente.

---

## ✨ Funcionalidades Principais
1.  **Monitoramento Dinâmico:** Funciona em qualquer URL, desde que o XPath ou Regex seja fornecido.
2.  **Validação Robusta:** Impede a execução com URLs inválidas ou nomes de usuário com menos de 3 caracteres.
3.  **Ação em Segunda Aba:** Ao detectar mudança, o robô abre uma nova aba e preenche um formulário público automaticamente.
4.  **Sistema de Logs Duplo:** Separação entre o histórico de ações do usuário e o histórico de variações de mercado.

---

## 🚀 Como Executar

1.  **Instale as dependências:**
    ```bash
    pip install selenium webdriver-manager
    ```
2.  **Inicie a aplicação:**
    ```bash
    python main.py
    ```
3.  **Execute os testes unitários:**
    ```bash
    python test_scraper.py
    ```

---

## 📄 Documentação Técnica
A documentação detalhada das funções foi gerada via **pydoc**. Para visualizar em formato HTML, utilize o comando:
```bash
python -m pydoc -w core.scraper core.monitor automation.action