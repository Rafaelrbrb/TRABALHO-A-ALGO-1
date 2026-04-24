🤖 Assistente de Lances para Leilão (Python Automation)
Este projeto consiste em um sistema inteligente de monitoramento de variáveis em páginas web de estrutura dinâmica. O software é capaz de identificar mudanças de preço em tempo real, calcular variações e interagir automaticamente com sistemas externos para registro de ocorrências.

👤 Identificação dos alunos
Nome: Leonardo // Rafael // Davi // Nikolas // Matheus // Artuhur

Projeto: Sistema de Monitoramento e Assistente de Lances

Versão: 1.0.0

🛠️ Arquitetura do Sistema
O projeto foi estruturado seguindo princípios de modularidade para facilitar a manutenção e garantir a escalabilidade:
.
├── automation/
│   ├── action.py      # Lógica de interação com páginas externas (httpbin)
│   └── browser.py     # Gerenciamento e configuração do Selenium WebDriver
├── core/
│   ├── monitor.py     # Loop principal de monitoramento e lógica de comparação
│   ├── scraper.py     # Extração e tratamento de dados (XPath e Regex)
│   └── validator.py   # Validação de entradas (URL, Timeout, Usuário)
├── interface/
│   └── gui.py         # Interface gráfica desenvolvida em Tkinter
├── logs/
│   ├── activity_log.txt # Registro histórico de todas as ações do usuário
│   └── price_log.txt    # Histórico detalhado de variações de preços detectadas
├── main.py            # Ponto de entrada (Entry point) do aplicativo
└── test_scraper.py    # Testes unitários para validação dos extratores

📈 Análise de Complexidade (Big O)

Um dos requisitos fundamentais do projeto é a compreensão da eficiência do algoritmo:

Busca de Elementos: A localização do preço via XPath ou Expressões Regulares (Regex) dentro do DOM (Document Object Model) possui complexidade de $O(N)$, onde $N$ representa o número total de nós/elementos no HTML da página.
Por que $O(N)$? Para encontrar um elemento específico em uma estrutura de árvore desconhecida, o motor do navegador precisa realizar uma varredura (traversal) que, no pior caso, visita todos os elementos até localizar o alvo.
Monitoramento: O loop de verificação é executado em tempo constante por ciclo, condicionado ao timeout definido pelo usuário.

✨ Funcionalidades Principais
Monitoramento Dinâmico: Funciona em qualquer URL (estrutura agnóstica), desde que o XPath ou Regex seja fornecido.

Validação Robusta: Impede a execução com URLs inválidas, nomes de usuário curtos (mínimo de 3 caracteres) ou timeouts não numéricos.

Ação em Segunda Aba: Ao detectar mudança, o sistema abre uma nova aba, preenche um formulário público e clica no botão de envio automaticamente.

Sistema de Logs Duplo: Separação clara entre o que o usuário faz e o que o mercado (preço) apresenta.

🚀 Como Executar
Instale as dependências:

Bash
pip install selenium webdriver-manager
Inicie a aplicação:

Bash
py main.py
Execute os testes unitários:

Bash
py test_scraper.py

🧪 Testes Automatizados
O projeto conta com testes unitários que garantem que a lógica de conversão de moeda (tratamento de pontos, vírgulas e símbolos de Real/Dólar) funcione corretamente antes de entrar em produção.

Nota: Este projeto foi desenvolvido para fins acadêmicos, respeitando as diretrizes de automação ética e tratamento de erros para evitar sobrecarga em servidores públicos.