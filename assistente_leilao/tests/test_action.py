import pytest
from unittest.mock import MagicMock, patch, call
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from assistente_leilao.automation.action import (
    inserir_valores,
    ACTION_URL,
    FIELD_SELECTOR,
    BUTTON_SELECTOR,
    WAIT_TIMEOUT
)


class TestInserirValores:
    """Testes para a função de inserir valores no formulário"""
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_sucesso(self, mock_wait_class):
        """Insere valores com sucesso no formulário"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        # Mock do campo de texto
        campo_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, MagicMock()]  # campo, botão
        
        inserir_valores(driver_mock, "R$ 100", "R$ 150")
        
        # Verifica se driver foi para a URL correta
        driver_mock.get.assert_called_once_with(ACTION_URL)
        
        # Verifica se limpa o campo
        campo_mock.clear.assert_called_once()
        
        # Verifica se escreve o valor correto
        campo_mock.send_keys.assert_called_once()
        texto_enviado = campo_mock.send_keys.call_args[0][0]
        assert "100" in texto_enviado
        assert "150" in texto_enviado
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_clica_botao(self, mock_wait_class):
        """Clica no botão de submit após preencher"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        botao_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, botao_mock]
        
        inserir_valores(driver_mock, "100", "150")
        
        # Verifica se clica no botão
        botao_mock.click.assert_called_once()
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_espera_campo_estar_presente(self, mock_wait_class):
        """Espera o campo estar presente antes de interagir"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        botao_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, botao_mock]
        
        inserir_valores(driver_mock, "100", "150")
        
        # Verifica se WebDriverWait foi criado com timeout correto
        mock_wait_class.assert_called_once_with(driver_mock, WAIT_TIMEOUT)
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_espera_botao_ser_clicavel(self, mock_wait_class):
        """Espera o botão ser clicável antes de clicar"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        botao_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, botao_mock]
        
        inserir_valores(driver_mock, "100", "150")
        
        # Deve chamar wait.until duas vezes
        assert mock_wait.until.call_count == 2
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_formato_mensagem(self, mock_wait_class):
        """Formata corretamente a mensagem com os valores"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, MagicMock()]
        
        valor_antigo = "R$ 1.000,00"
        valor_novo = "R$ 2.500,00"
        inserir_valores(driver_mock, valor_antigo, valor_novo)
        
        # Extrai o argumento enviado
        chamada = campo_mock.send_keys.call_args[0][0]
        assert "Valor antigo:" in chamada
        assert "Valor novo:" in chamada
        assert valor_antigo in chamada
        assert valor_novo in chamada
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_numeros_grandes(self, mock_wait_class):
        """Funciona com valores grandes"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, MagicMock()]
        
        inserir_valores(driver_mock, "9.999.999,99", "10.000.000,00")
        
        campo_mock.clear.assert_called_once()
        campo_mock.send_keys.assert_called_once()
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_limpa_campo_antes_escrever(self, mock_wait_class):
        """Limpa o campo antes de escrever novos valores"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, MagicMock()]
        
        inserir_valores(driver_mock, "100", "200")
        
        # Verifica que clear foi chamado
        campo_mock.clear.assert_called_once()
        # Verifica que send_keys foi chamado
        campo_mock.send_keys.assert_called_once()
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_com_valores_especiais(self, mock_wait_class):
        """Funciona com valores contendo caracteres especiais"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, MagicMock()]
        
        # Valores com símbolos especiais
        inserir_valores(driver_mock, "R$ 100,50", "R$ 150,75")
        
        campo_mock.send_keys.assert_called_once()
        texto = campo_mock.send_keys.call_args[0][0]
        assert "100,50" in texto
        assert "150,75" in texto
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_seleciona_url_correta(self, mock_wait_class):
        """Navega para a URL correta do formulário"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        mock_wait.until.side_effect = [MagicMock(), MagicMock()]
        
        inserir_valores(driver_mock, "100", "200")
        
        # Verifica se vai para a URL correta
        driver_mock.get.assert_called_once()
        url_chamada = driver_mock.get.call_args[0][0]
        assert url_chamada == ACTION_URL
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_sequence_correta(self, mock_wait_class):
        """Executa as operações na sequência correta"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        botao_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, botao_mock]
        
        inserir_valores(driver_mock, "100", "200")
        
        # Sequência: driver.get -> campo.clear -> campo.send_keys -> botao.click
        # Pode verificar isso através de mock_calls
        assert driver_mock.get.call_count == 1
        assert campo_mock.clear.call_count == 1
        assert campo_mock.send_keys.call_count == 1
        assert botao_mock.click.call_count == 1
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_campo_com_valor_previo(self, mock_wait_class):
        """Limpa campo com valor prévio antes de escrever novo"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        campo_mock.text = "valor antigo"  # Campo com valor prévio
        mock_wait.until.side_effect = [campo_mock, MagicMock()]
        
        inserir_valores(driver_mock, "novo_antigo", "novo_novo")
        
        # Clear deve ser chamado para limpar valor prévio
        campo_mock.clear.assert_called_once()
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_com_valores_string_vazia(self, mock_wait_class):
        """Funciona com valores vazios"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, MagicMock()]
        
        inserir_valores(driver_mock, "", "")
        
        campo_mock.send_keys.assert_called_once()
        texto = campo_mock.send_keys.call_args[0][0]
        assert "Valor antigo:" in texto
        assert "Valor novo:" in texto
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_timeout_espera(self, mock_wait_class):
        """WebDriverWait usa timeout correto"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, MagicMock()]
        
        inserir_valores(driver_mock, "100", "200")
        
        # Verifica timeout
        mock_wait_class.assert_called_once_with(driver_mock, WAIT_TIMEOUT)
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_clica_apos_preencher(self, mock_wait_class):
        """Clica no botão após preencher o campo"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        botao_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, botao_mock]
        
        inserir_valores(driver_mock, "100", "200")
        
        # Verifica ordem: clear → send_keys → click
        assert campo_mock.clear.called
        assert campo_mock.send_keys.called
        assert botao_mock.click.called
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_com_caracteres_especiais(self, mock_wait_class):
        """Funciona com caracteres especiais"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, MagicMock()]
        
        valor_antigo = "R$ 1.000,00 #!@$%"
        valor_novo = "R$ 2.000,00 @#$!"
        inserir_valores(driver_mock, valor_antigo, valor_novo)
        
        texto = campo_mock.send_keys.call_args[0][0]
        assert valor_antigo in texto
        assert valor_novo in texto
    
    @patch('assistente_leilao.automation.action.WebDriverWait')
    def test_inserir_valores_espera_elemento_presente(self, mock_wait_class):
        """Espera elemento estar presente antes de interagir"""
        driver_mock = MagicMock()
        mock_wait = MagicMock()
        mock_wait_class.return_value = mock_wait
        
        campo_mock = MagicMock()
        botao_mock = MagicMock()
        mock_wait.until.side_effect = [campo_mock, botao_mock]
        
        inserir_valores(driver_mock, "100", "200")
        
        # until deve ser chamado 2 vezes (campo e botão)
        assert mock_wait.until.call_count == 2
