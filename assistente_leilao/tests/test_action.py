import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, call


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def install_fake_selenium():
    selenium = types.ModuleType("selenium")
    webdriver = types.ModuleType("selenium.webdriver")
    webdriver_common = types.ModuleType("selenium.webdriver.common")
    by_module = types.ModuleType("selenium.webdriver.common.by")
    webdriver_support = types.ModuleType("selenium.webdriver.support")
    ui_module = types.ModuleType("selenium.webdriver.support.ui")
    ec_module = types.ModuleType("selenium.webdriver.support.expected_conditions")

    class By:
        NAME = "name"
        CSS_SELECTOR = "css selector"

    by_module.By = By
    ui_module.WebDriverWait = object
    ec_module.presence_of_element_located = lambda locator: locator
    ec_module.element_to_be_clickable = lambda locator: locator

    sys.modules["selenium"] = selenium
    sys.modules["selenium.webdriver"] = webdriver
    sys.modules["selenium.webdriver.common"] = webdriver_common
    sys.modules["selenium.webdriver.common.by"] = by_module
    sys.modules["selenium.webdriver.support"] = webdriver_support
    sys.modules["selenium.webdriver.support.ui"] = ui_module
    sys.modules["selenium.webdriver.support.expected_conditions"] = ec_module


def load_action_module():
    install_fake_selenium()
    sys.modules.pop("assistente_leilao.automation.action", None)
    return importlib.import_module("assistente_leilao.automation.action")


class ActionTests(unittest.TestCase):
    def setUp(self):
        self.action = load_action_module()

    def test_inserir_valores_preenche_formulario_e_submete(self):
        driver = Mock()
        campo = Mock()
        botao = Mock()
        wait = Mock()
        wait.until.side_effect = [campo, botao]

        self.action.WebDriverWait = Mock(return_value=wait)
        self.action.EC.presence_of_element_located = Mock(return_value="campo")
        self.action.EC.element_to_be_clickable = Mock(return_value="botao")

        self.action.inserir_valores(driver, 10.0, 12.5)

        driver.get.assert_called_once_with(self.action.ACTION_URL)
        self.action.WebDriverWait.assert_called_once_with(driver, self.action.WAIT_TIMEOUT)
        self.action.EC.presence_of_element_located.assert_called_once_with(self.action.FIELD_SELECTOR)
        self.action.EC.element_to_be_clickable.assert_called_once_with(self.action.BUTTON_SELECTOR)
        self.assertEqual(wait.until.call_args_list, [call("campo"), call("botao")])
        campo.clear.assert_called_once_with()
        campo.send_keys.assert_called_once_with("Valor antigo: 10.0 | Valor novo: 12.5")
        botao.click.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
