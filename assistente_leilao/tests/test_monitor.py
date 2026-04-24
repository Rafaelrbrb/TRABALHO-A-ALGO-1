import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def load_monitor_module():
    fake_scraper = types.ModuleType("assistente_leilao.core.scraper")
    fake_scraper.obter_preco = Mock(return_value=None)

    fake_price_log = types.ModuleType("assistente_leilao.logs.price_log")
    fake_price_log.registrar_mudanca = Mock()

    sys.modules["assistente_leilao.core.scraper"] = fake_scraper
    sys.modules["assistente_leilao.logs.price_log"] = fake_price_log
    sys.modules.pop("assistente_leilao.core.monitor", None)
    return importlib.import_module("assistente_leilao.core.monitor")


class MonitorTests(unittest.TestCase):
    def setUp(self):
        self.monitor = load_monitor_module()
        self.driver = Mock()

    def test_monitorar_para_se_preco_inicial_nao_for_encontrado(self):
        callback = Mock()
        self.monitor.obter_preco = Mock(return_value=None)
        self.monitor.registrar_mudanca = Mock()
        self.monitor.time.sleep = Mock()

        self.monitor.monitorar(self.driver, "//span", "", 5, callback=callback)

        self.monitor.time.sleep.assert_not_called()
        self.driver.refresh.assert_not_called()
        self.monitor.registrar_mudanca.assert_not_called()
        callback.assert_not_called()

    def test_monitorar_registra_mudanca_e_callback_quando_preco_muda(self):
        callback = Mock()
        self.monitor.obter_preco = Mock(side_effect=[100.0, 95.5])
        self.monitor.registrar_mudanca = Mock()
        self.monitor.time.sleep = Mock(side_effect=[None, KeyboardInterrupt])

        self.monitor.monitorar(self.driver, "//span", "", 5, callback=callback)

        self.driver.refresh.assert_called_once_with()
        self.monitor.registrar_mudanca.assert_called_once_with(100.0, 95.5)
        callback.assert_called_once_with(preco_antigo=100.0, preco_novo=95.5)

    def test_monitorar_ignora_leitura_invalida_e_tenta_novamente(self):
        callback = Mock()
        self.monitor.obter_preco = Mock(side_effect=[100.0, None])
        self.monitor.registrar_mudanca = Mock()
        self.monitor.time.sleep = Mock(side_effect=[None, KeyboardInterrupt])

        self.monitor.monitorar(self.driver, "//span", "", 5, callback=callback)

        self.driver.refresh.assert_called_once_with()
        self.monitor.registrar_mudanca.assert_not_called()
        callback.assert_not_called()

    def test_monitorar_nao_registra_quando_preco_permanece_igual(self):
        callback = Mock()
        self.monitor.obter_preco = Mock(side_effect=[100.0, 100.0])
        self.monitor.registrar_mudanca = Mock()
        self.monitor.time.sleep = Mock(side_effect=[None, KeyboardInterrupt])

        self.monitor.monitorar(self.driver, "//span", "", 5, callback=callback)

        self.driver.refresh.assert_called_once_with()
        self.monitor.registrar_mudanca.assert_not_called()
        callback.assert_not_called()

    def test_monitorar_respeita_evento_de_parada_sem_atualizar_pagina(self):
        callback = Mock()
        status_callback = Mock()
        stop_event = Mock()
        stop_event.is_set.side_effect = [False, True]
        stop_event.wait.return_value = True

        self.monitor.obter_preco = Mock(return_value=100.0)
        self.monitor.registrar_mudanca = Mock()
        self.monitor.time.sleep = Mock()

        self.monitor.monitorar(
            self.driver,
            "//span",
            "",
            5,
            callback=callback,
            stop_event=stop_event,
            status_callback=status_callback,
        )

        stop_event.wait.assert_called_once_with(5)
        self.monitor.time.sleep.assert_not_called()
        self.driver.refresh.assert_not_called()
        self.monitor.registrar_mudanca.assert_not_called()
        callback.assert_not_called()
        status_callback.assert_called_once_with("Monitoramento encerrado pelo usuário.")


if __name__ == "__main__":
    unittest.main()
