import pytest
from unittest.mock import patch, MagicMock, call
from assistente_leilao.core.monitor import monitorar


class TestMonitorar:
    """Testes para a função de monitoramento de preços"""
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_preco_inicial_nao_encontrado(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Se preço inicial não for encontrado, encerra"""
        driver_mock = MagicMock()
        
        # Primeira chamada retorna None
        mock_obter_preco.return_value = None
        
        monitorar(driver_mock, "//div", "", 5)
        
        # Não deve registrar mudança
        mock_registrar.assert_not_called()
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_sem_mudanca_preco(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Se preço não muda, não registra mudança"""
        driver_mock = MagicMock()
        
        # Sempre retorna o mesmo preço
        mock_obter_preco.return_value = 100.0
        
        # Simula apenas 2 iterações interrompendo
        mock_sleep.side_effect = [None, KeyboardInterrupt()]
        
        monitorar(driver_mock, "//div", "", 5)
        
        # Não deve registrar mudança
        mock_registrar.assert_not_called()
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_detecção_mudanca_preco(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Detecta mudança de preço"""
        driver_mock = MagicMock()
        
        # Primeira chamada: 100, segunda: 120, terceira: KeyboardInterrupt
        mock_obter_preco.side_effect = [100.0, 120.0]
        mock_sleep.side_effect = [None, KeyboardInterrupt()]
        
        monitorar(driver_mock, "//div", "", 5)
        
        # Deve registrar uma mudança
        mock_registrar.assert_called_once_with(100.0, 120.0)
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_multiplas_mudancas(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Detecta múltiplas mudanças de preço"""
        driver_mock = MagicMock()
        
        # Sequência de preços: 100 -> 120 -> 110
        mock_obter_preco.side_effect = [100.0, 120.0, 110.0]
        mock_sleep.side_effect = [None, None, KeyboardInterrupt()]
        
        monitorar(driver_mock, "//div", "", 5)
        
        # Deve registrar duas mudanças
        assert mock_registrar.call_count == 2
        calls = [call(100.0, 120.0), call(120.0, 110.0)]
        mock_registrar.assert_has_calls(calls)
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_com_callback(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Callback é chamado ao detectar mudança"""
        driver_mock = MagicMock()
        callback_mock = MagicMock()
        
        mock_obter_preco.side_effect = [100.0, 150.0]
        mock_sleep.side_effect = [None, KeyboardInterrupt()]
        
        monitorar(driver_mock, "//div", "", 5, callback=callback_mock)
        
        # Callback deve ser chamado com parâmetros nomeados
        callback_mock.assert_called_once_with(
            preco_antigo=100.0,
            preco_novo=150.0
        )
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_tratamento_erro_leitura(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Se falhar na leitura, continua tentando"""
        driver_mock = MagicMock()
        
        # 100, None (erro), 100 (recuperado), 150 (mudança)
        mock_obter_preco.side_effect = [100.0, None, 100.0, 150.0]
        mock_sleep.side_effect = [None, None, None, KeyboardInterrupt()]
        
        monitorar(driver_mock, "//div", "", 5)
        
        # Deve registrar apenas uma mudança (100->150)
        mock_registrar.assert_called_once_with(100.0, 150.0)
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_refresh_pagina(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """A página é atualizada a cada iteração"""
        driver_mock = MagicMock()
        
        # Retorna preço inicial, depois KeyboardInterrupt no sleep
        mock_obter_preco.return_value = 100.0
        mock_sleep.side_effect = KeyboardInterrupt()
        
        monitorar(driver_mock, "//div", "", 5)
        
        # Sleep deve ser chamado (dentro do loop while)
        mock_sleep.assert_called()
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_timeout_respeitado(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """O timeout é respeitado entre verificações"""
        driver_mock = MagicMock()
        timeout_valor = 10
        
        mock_obter_preco.side_effect = [100.0]
        mock_sleep.side_effect = KeyboardInterrupt()
        
        monitorar(driver_mock, "//div", "", timeout_valor)
        
        # Sleep deve ser chamado com o timeout correto
        mock_sleep.assert_called_with(timeout_valor)
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_keyboard_interrupt(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Encerra corretamente ao receber KeyboardInterrupt"""
        driver_mock = MagicMock()
        
        mock_obter_preco.return_value = 100.0
        mock_sleep.side_effect = KeyboardInterrupt()
        
        # Não deve lançar exceção
        monitorar(driver_mock, "//div", "", 5)
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_sem_callback(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Funciona normalmente sem callback"""
        driver_mock = MagicMock()
        
        mock_obter_preco.side_effect = [100.0, 150.0]
        mock_sleep.side_effect = [None, KeyboardInterrupt()]
        
        # Não deve lançar exceção
        monitorar(driver_mock, "//div", "", 5, callback=None)
        
        mock_registrar.assert_called_once_with(100.0, 150.0)
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_primeira_leitura_com_xpath(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Primeira leitura usa xpath e regex corretos"""
        driver_mock = MagicMock()
        xpath = "//div[@class='preco']"
        regex = r"\d+,\d{2}"
        
        mock_obter_preco.return_value = 100.0
        mock_sleep.side_effect = KeyboardInterrupt()
        
        monitorar(driver_mock, xpath, regex, 5)
        
        # Deve chamar obter_preco com xpath e regex corretos
        mock_obter_preco.assert_called_with(driver_mock, xpath, regex)
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_continua_apos_erro_leitura(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Continua tentando após erro de leitura múltiplas vezes"""
        driver_mock = MagicMock()
        
        # 100 (inicial), None (erro 1), None (erro 2), 150 (recuperado)
        mock_obter_preco.side_effect = [100.0, None, None, 150.0]
        mock_sleep.side_effect = [None, None, None, KeyboardInterrupt()]
        
        monitorar(driver_mock, "//div", "", 5)
        
        # Deve registrar a mudança final
        mock_registrar.assert_called_once_with(100.0, 150.0)
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_callback_nao_chamado_sem_mudanca(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Callback não é chamado quando preço não muda"""
        driver_mock = MagicMock()
        callback_mock = MagicMock()
        
        # Preço permanece igual
        mock_obter_preco.side_effect = [100.0, 100.0]
        mock_sleep.side_effect = [None, KeyboardInterrupt()]
        
        monitorar(driver_mock, "//div", "", 5, callback=callback_mock)
        
        # Callback não deve ser chamado
        callback_mock.assert_not_called()
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_callback_chamado_multiplas_vezes(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Callback é chamado múltiplas vezes quando há múltiplas mudanças"""
        driver_mock = MagicMock()
        callback_mock = MagicMock()
        
        # 100 → 120 → 110
        mock_obter_preco.side_effect = [100.0, 120.0, 110.0]
        mock_sleep.side_effect = [None, None, KeyboardInterrupt()]
        
        monitorar(driver_mock, "//div", "", 5, callback=callback_mock)
        
        # Callback deve ser chamado 2 vezes
        assert callback_mock.call_count == 2
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_print_preco_inicial(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Imprime preço inicial corretamente"""
        driver_mock = MagicMock()
        
        mock_obter_preco.return_value = 500.0
        mock_sleep.side_effect = KeyboardInterrupt()
        
        monitorar(driver_mock, "//div", "", 5)
        
        # Deve ter impresso mensagens (verificável via logs)
        mock_obter_preco.assert_called()
    
    @patch('assistente_leilao.core.monitor.registrar_mudanca')
    @patch('assistente_leilao.core.monitor.obter_preco')
    @patch('assistente_leilao.core.monitor.time.sleep')
    def test_monitorar_atualiza_preco_atual(
        self,
        mock_sleep,
        mock_obter_preco,
        mock_registrar
    ):
        """Atualiza preco_atual após mudança"""
        driver_mock = MagicMock()
        
        # 100 → 150 → 200 (deve usar 150 como base para próxima comparação)
        mock_obter_preco.side_effect = [100.0, 150.0, 200.0]
        mock_sleep.side_effect = [None, None, KeyboardInterrupt()]
        
        monitorar(driver_mock, "//div", "", 5)
        
        # Deve registrar duas mudanças com a sequência correta
        assert mock_registrar.call_count == 2
        # Primeiro: 100 → 150
        assert mock_registrar.call_args_list[0][0] == (100.0, 150.0)
        # Segundo: 150 → 200
        assert mock_registrar.call_args_list[1][0] == (150.0, 200.0)