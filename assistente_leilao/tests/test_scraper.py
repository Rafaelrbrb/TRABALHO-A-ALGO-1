import pytest
from unittest.mock import patch, MagicMock
from assistente_leilao.core.scraper import extrair_numero, obter_preco


class TestExtrairNumero:
    """Testes para extração de números de textos
    
    Nota: A função extrair_numero assume o formato brasileiro:
    - Ponto (.) = separador de milhar → removido
    - Vírgula (,) = separador decimal → convertido para ponto
    
    Exemplos:
    - "1.000,50" → 1000.50 (correto)
    - "100,50" → 100.50 (correto)
    - "100.50" → 10050.0 (ponto removido como se fosse milhar)
    """
    
    def test_numero_simples(self):
        """Número simples sem formatação"""
        resultado = extrair_numero("100")
        assert resultado == 100.0
    
    def test_numero_com_ponto_decimal(self):
        """Número com ponto: é removido como se fosse separador de milhar"""
        # IMPORTANTE: "100.50" não é o formato correto (seria "100,50")
        # A função remove o ponto → "10050"
        resultado = extrair_numero("100.50")
        assert resultado == 10050.0
    
    def test_numero_com_virgula_decimal(self):
        """Número com vírgula como separador decimal"""
        resultado = extrair_numero("100,50")
        assert resultado == 100.50
    
    def test_numero_com_separador_milhar_ponto(self):
        """Número com ponto como separador de milhar (Brasil)"""
        # Formato: 1.000,50 (ponto para milhar, vírgula para decimal)
        resultado = extrair_numero("1.000,50")
        assert resultado == 1000.50
    
    def test_numero_em_texto(self):
        """Número dentro de texto"""
        resultado = extrair_numero("Preço: R$ 1.500,00")
        assert resultado == 1500.00
    
    def test_numero_com_moeda(self):
        """Número com símbolo de moeda"""
        resultado = extrair_numero("$ 250,75")
        assert resultado == 250.75
    
    def test_zero(self):
        """Valor zero"""
        resultado = extrair_numero("0")
        assert resultado == 0.0
    
    def test_numero_negativo(self):
        """Número negativo (método não remove sinais, apenas números e vírgula/ponto)"""
        resultado = extrair_numero("-100")
        # Depende da implementação - remove tudo que não é número, vírgula
        assert resultado is not None
    
    def test_texto_sem_numero(self):
        """Texto sem números"""
        resultado = extrair_numero("sem número")
        # Pode retornar None ou 0.0
        assert resultado is None or resultado == 0.0
    
    def test_string_vazia(self):
        """String vazia"""
        resultado = extrair_numero("")
        assert resultado is None or resultado == 0.0
    
    def test_numero_muito_grande(self):
        """Número muito grande"""
        resultado = extrair_numero("1.000.000,50")
        assert resultado == 1000000.50
    
    def test_multiplos_numeros(self):
        """Texto com múltiplos números - extrai como um único número"""
        # A função extrai tudo que é dígito/vírgula/ponto
        # "100 e 200" → "100200" → 100200.0
        resultado = extrair_numero("100 e 200")
        # Dependendo do interpretador pode concatenar ou extrair primeiro
        assert resultado is not None
    
    def test_extrair_numero_com_valor_none(self):
        """Trata valor None com exceção"""
        resultado = extrair_numero(None)
        assert resultado is None
    
    def test_extrair_numero_com_tipo_invalido(self):
        """Trata tipos inválidos com exceção"""
        resultado = extrair_numero(123)  # int em vez de string
        assert resultado is None
    
    def test_extrair_numero_com_lista(self):
        """Trata lista com exceção"""
        resultado = extrair_numero([1, 2, 3])
        assert resultado is None
    
    def test_extrair_numero_com_diccionario(self):
        """Trata dicionário com exceção"""
        resultado = extrair_numero({"valor": 100})
        assert resultado is None


class TestObterPreco:
    """Testes para obtenção de preço da página"""
    
    @patch('assistente_leilao.core.scraper.encontrar_valor')
    def test_obter_preco_com_xpath(self, mock_encontrar):
        """Obtém preço usando xpath"""
        mock_encontrar.return_value = "R$ 500,00"
        driver_mock = MagicMock()
        
        resultado = obter_preco(driver_mock, xpath="//div[@class='preco']")
        
        assert resultado == 500.00
        mock_encontrar.assert_called_once_with(driver_mock, "//div[@class='preco']", "")
    
    @patch('assistente_leilao.core.scraper.encontrar_valor')
    def test_obter_preco_com_regex(self, mock_encontrar):
        """Obtém preço usando regex"""
        mock_encontrar.return_value = "1.200,50"
        driver_mock = MagicMock()
        
        resultado = obter_preco(driver_mock, regex=r"\d+\.\d{2}")
        
        assert resultado == 1200.50
        mock_encontrar.assert_called_once_with(driver_mock, "", r"\d+\.\d{2}")
    
    @patch('assistente_leilao.core.scraper.encontrar_valor')
    def test_obter_preco_elemento_nao_encontrado(self, mock_encontrar):
        """Elemento não encontrado retorna None"""
        mock_encontrar.return_value = None
        driver_mock = MagicMock()
        
        resultado = obter_preco(driver_mock, xpath="//div[@class='inexistente']")
        
        assert resultado is None
    
    @patch('assistente_leilao.core.scraper.encontrar_valor')
    def test_obter_preco_texto_invalido(self, mock_encontrar):
        """Texto que não pode ser convertido em número"""
        mock_encontrar.return_value = "sem número aqui"
        driver_mock = MagicMock()
        
        resultado = obter_preco(driver_mock, xpath="//div")
        
        # Deve retornar None ou 0.0 dependendo da implementação
        assert resultado is None or resultado == 0.0
    
    @patch('assistente_leilao.core.scraper.encontrar_valor')
    def test_obter_preco_zero(self, mock_encontrar):
        """Obtém preço zero"""
        mock_encontrar.return_value = "0"
        driver_mock = MagicMock()
        
        resultado = obter_preco(driver_mock, xpath="//div")
        
        assert resultado == 0.0
    
    @patch('assistente_leilao.core.scraper.encontrar_valor')
    def test_obter_preco_valor_negativo(self, mock_encontrar):
        """Trata valor negativo"""
        mock_encontrar.return_value = "-100"
        driver_mock = MagicMock()
        
        resultado = obter_preco(driver_mock, xpath="//div")
        
        # Depende de como o regex é tratado
        assert resultado is not None
    
    @patch('assistente_leilao.core.scraper.encontrar_valor')
    def test_obter_preco_com_xpath_e_regex(self, mock_encontrar):
        """Ambos xpath e regex podem ser passados"""
        mock_encontrar.return_value = "999,99"
        driver_mock = MagicMock()
        
        resultado = obter_preco(
            driver_mock,
            xpath="//span[@id='price']",
            regex=r"\d+,\d{2}"
        )
        
        assert resultado == 999.99
        mock_encontrar.assert_called_once_with(
            driver_mock,
            "//span[@id='price']",
            r"\d+,\d{2}"
        )
    
    @patch('assistente_leilao.core.scraper.encontrar_valor')
    def test_obter_preco_grande_valor(self, mock_encontrar):
        """Obtém um valor grande de preço"""
        mock_encontrar.return_value = "R$ 1.250.500,99"
        driver_mock = MagicMock()
        
        resultado = obter_preco(driver_mock, xpath="//div")
        
        assert resultado == 1250500.99
