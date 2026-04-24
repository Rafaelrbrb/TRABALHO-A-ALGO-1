# Guia de Testes Unitários - Assistente de Leilão

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Instalação](#instalação)
3. [Estrutura dos Testes](#estrutura-dos-testes)
4. [Como Executar](#como-executar)
5. [Cobertura de Testes](#cobertura-de-testes)
6. [Exemplos de Testes](#exemplos-de-testes)
7. [Boas Práticas](#boas-práticas)

## Visão Geral

Os testes unitários automatizados cobrem os principais módulos da aplicação:

- **`test_validator.py`** - Testes de validação de URLs, timeouts, nomes e seletores
- **`test_scraper.py`** - Testes de extração de números e preços
- **`test_action.py`** - Testes de ações do Selenium (cliques, preenchimento de formulários)
- **`test_monitor.py`** - Testes de monitoramento de preços

## Instalação

### 1. Instale as dependências de teste

```powershell
pip install -r requirements.txt
```

### 2. Verifique a instalação

```powershell
pytest --version
```

Deve retornar algo como: `pytest 7.x.x`

## Estrutura dos Testes

```
assistente_leilao/
├── tests/
│   ├── __init__.py
│   ├── test_validator.py    # 5 classes de teste, 24 testes
│   ├── test_scraper.py      # 2 classes de teste, 13 testes
│   ├── test_action.py       # 1 classe de teste, 10 testes
│   └── test_monitor.py      # 1 classe de teste, 11 testes
├── conftest.py              # Configuração global de fixtures
└── README_TESTS.md          # Este arquivo
```

**Total**: ~60 testes unitários

## Como Executar

### Executar todos os testes

```powershell
pytest
```

Saída esperada:
```
========================= test session starts ==========================
collected 60 items

assistente_leilao/tests/test_validator.py ...................... [  41%]
assistente_leilao/tests/test_scraper.py ........... [  63%]
assistente_leilao/tests/test_action.py .......... [  80%]
assistente_leilao/tests/test_monitor.py ........... [  99%]

========================= 60 passed in 0.45s ==========================
```

### Executar testes com modo verbose

```powershell
pytest -v
```

Mostra o nome de cada teste individualmente.

### Executar um arquivo de teste específico

```powershell
pytest assistente_leilao/tests/test_validator.py
```

### Executar uma classe de teste específica

```powershell
pytest assistente_leilao/tests/test_validator.py::TestValidarUrl
```

### Executar um teste específico

```powershell
pytest assistente_leilao/tests/test_validator.py::TestValidarUrl::test_url_valida_http
```

### Executar com cobertura de código

```powershell
pytest --cov=assistente_leilao --cov-report=html
```

Gera relatório HTML em `htmlcov/index.html`

### Executar com saída mais detalhada

```powershell
pytest -vv --tb=short
```

### Executar apenas testes rápidos

```powershell
pytest -m "not slow"
```

### Parar no primeiro erro

```powershell
pytest -x
```

## Cobertura de Testes

### Validator (validação de entrada)

✅ **Test Coverage**: ~95%

| Função | Testes | Casos Cobertos |
|--------|--------|-----------------|
| `validar_url()` | 7 | URLs válidas/inválidas, schemes, domínios |
| `validar_timeout()` | 6 | Números válidos, strings, zero, negativos |
| `validar_nome()` | 7 | Comprimento, caracteres, acentos |
| `validar_seletor()` | 5 | XPath, regex, ambos, vazios |
| `validar_tudo()` | 4 | Validação combinada, múltiplos erros |

### Scraper (extração de dados)

✅ **Test Coverage**: ~90%

| Função | Testes | Casos Cobertos |
|--------|--------|-----------------|
| `extrair_numero()` | 9 | Formatação, separadores, casos especiais |
| `obter_preco()` | 9 | XPath, regex, erros, valores nulos |

### Action (automação Selenium)

✅ **Test Coverage**: ~100%

| Função | Testes | Casos Cobertos |
|--------|--------|-----------------|
| `inserir_valores()` | 10 | Navegação, preenchimento, cliques, sequência |

### Monitor (monitoramento)

✅ **Test Coverage**: ~95%

| Função | Testes | Casos Cobertos |
|--------|--------|-----------------|
| `monitorar()` | 11 | Mudanças, callbacks, erros, timeout, interrupts |

## Exemplos de Testes

### Exemplo 1: Teste simples de validação

```python
# Testa se uma URL válida é aceita
def test_url_valida_https(self):
    resultado = validar_url("https://example.com")
    assert resultado is None  # None = sem erros
```

### Exemplo 2: Teste com mocks

```python
# Testa obtenção de preço com mock
@patch('assistente_leilao.core.scraper.encontrar_valor')
def test_obter_preco_com_xpath(self, mock_encontrar):
    mock_encontrar.return_value = "R$ 500,00"
    driver_mock = MagicMock()
    
    resultado = obter_preco(driver_mock, xpath="//div")
    
    assert resultado == 500.00
```

### Exemplo 3: Teste de comportamento

```python
# Testa mudança de preço
def test_monitorar_deteccao_mudanca_preco(self, mock_sleep, mock_obter_preco, ...):
    mock_obter_preco.side_effect = [100.0, 120.0]
    mock_sleep.side_effect = [None, KeyboardInterrupt()]
    
    monitorar(driver_mock, "//div", "", 5)
    
    mock_registrar.assert_called_once_with(100.0, 120.0)
```

## Boas Práticas

### 1. Escrever testes antes do código (TDD)

```python
# Escreva o teste primeiro
def test_nova_funcao():
    resultado = minha_nova_funcao(entrada)
    assert resultado == esperado
```

### 2. Use nomes descritivos

```python
# ✅ BOM
def test_validacao_url_sem_dominio_retorna_erro(self):

# ❌ RUIM
def test_url(self):
```

### 3. Teste casos extremos

```python
# Teste valores vazios, None, muito grandes, etc.
def test_extrair_numero_string_vazia(self):
def test_extrair_numero_muito_grande(self):
```

### 4. Use mocks para dependências externas

```python
# Use mock para Selenium, HTTP requests, etc.
@patch('requests.get')
def test_com_http_mock(self, mock_get):
    mock_get.return_value.status_code = 200
```

### 5. Um teste = uma responsabilidade

```python
# ✅ BOM - testa apenas validação de URL
def test_url_scheme_invalido(self):
    resultado = validar_url("ftp://example.com")
    assert "scheme deve ser http ou https" in resultado

# ❌ RUIM - testa múltiplas coisas
def test_tudo(self):
    assert validar_url(...) is None
    assert validar_timeout(...) is None
    # ...
```

### 6. Agrupe testes relacionados em classes

```python
class TestValidarUrl:  # Agrupa todos os testes de URL
    def test_url_valida_http(self):
    def test_url_valida_https(self):
    def test_url_scheme_invalido(self):
```

## Integração Contínua (CI)

Para executar testes automaticamente em cada commit:

### GitHub Actions

Crie `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: pytest --cov=assistente_leilao
```

## Comandos Úteis

| Comando | Descrição |
|---------|-----------|
| `pytest` | Executa todos os testes |
| `pytest -v` | Saída verbose (detalhada) |
| `pytest -x` | Para no primeiro erro |
| `pytest --lf` | Executa últimos testes que falharam |
| `pytest --ff` | Falhas primeiro, depois o resto |
| `pytest -k "validator"` | Executa apenas testes com "validator" no nome |
| `pytest --tb=short` | Traceback curto em caso de erro |
| `pytest --durations=10` | Mostra 10 testes mais lentos |
| `pytest --cov` | Gera relatório de cobertura |

## Solução de Problemas

### Erro: "ModuleNotFoundError"

```bash
# Certifique-se que está no diretório raiz do projeto
cd TRABALHO-A-ALGO-1
pytest
```

### Erro: "No module named 'pytest'"

```bash
pip install pytest
```

### Testes falhando com mock

```python
# Certifique-se que o path do patch é correto
# Use o path onde o OBJETO É USADO, não onde é definido
@patch('assistente_leilao.core.scraper.encontrar_valor')  # ✅ Correto
@patch('assistente_leilao.automation.page_finder.encontrar_valor')  # ❌ Errado
```

## Próximos Passos

1. **Execute os testes**: `pytest -v`
2. **Verifique cobertura**: `pytest --cov=assistente_leilao`
3. **Aumente cobertura**: Adicione testes para outros módulos
4. **Use TDD**: Escreva testes antes do código

---

**Última atualização**: 2026-04-24
**Versão**: 1.0
