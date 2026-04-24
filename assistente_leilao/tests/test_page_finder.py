import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def install_fake_page_finder_dependencies():
    selenium = types.ModuleType("selenium")
    webdriver = types.ModuleType("selenium.webdriver")
    webdriver_common = types.ModuleType("selenium.webdriver.common")
    by_module = types.ModuleType("selenium.webdriver.common.by")
    webdriver_support = types.ModuleType("selenium.webdriver.support")
    ui_module = types.ModuleType("selenium.webdriver.support.ui")
    ec_module = types.ModuleType("selenium.webdriver.support.expected_conditions")

    class By:
        XPATH = "xpath"

    by_module.By = By
    ui_module.WebDriverWait = Mock()
    ec_module.presence_of_element_located = Mock(side_effect=lambda locator: locator)

    sys.modules["selenium"] = selenium
    sys.modules["selenium.webdriver"] = webdriver
    sys.modules["selenium.webdriver.common"] = webdriver_common
    sys.modules["selenium.webdriver.common.by"] = by_module
    sys.modules["selenium.webdriver.support"] = webdriver_support
    sys.modules["selenium.webdriver.support.ui"] = ui_module
    sys.modules["selenium.webdriver.support.expected_conditions"] = ec_module

    return ui_module, ec_module


def load_page_finder_module():
    ui_module, ec_module = install_fake_page_finder_dependencies()
    sys.modules.pop("assistente_leilao.automation.page_finder", None)
    module = importlib.import_module("assistente_leilao.automation.page_finder")
    module._compilar_regex.cache_clear()
    return module, ui_module, ec_module


class PageFinderTests(unittest.TestCase):
    def setUp(self):
        self.page_finder, self.ui_module, self.ec_module = load_page_finder_module()

    def test_busca_por_xpath_usa_timeout_curto_e_polling_rapido(self):
        driver = Mock()
        element = Mock()
        element.text = " R$ 42,00 "
        wait = Mock()
        wait.until.return_value = element

        self.page_finder.WebDriverWait = Mock(return_value=wait)

        texto = self.page_finder._buscar_por_xpath(driver, "//span")

        self.assertEqual(texto, "R$ 42,00")
        self.page_finder.WebDriverWait.assert_called_once_with(
            driver,
            self.page_finder.WAIT_TIMEOUT,
            poll_frequency=self.page_finder.WAIT_POLL_FREQUENCY,
        )
        self.page_finder.EC.presence_of_element_located.assert_called_once_with(("xpath", "//span"))

    def test_busca_por_regex_retorna_match(self):
        driver = Mock()
        driver.page_source = "<span>R$ 123,45</span>"

        texto = self.page_finder._buscar_por_regex(driver, r"R\$ \d+,\d+")

        self.assertEqual(texto, "R$ 123,45")

    def test_busca_por_regex_retorna_none_para_regex_invalida(self):
        driver = Mock()
        driver.page_source = "<span>R$ 123,45</span>"

        texto = self.page_finder._buscar_por_regex(driver, "(")

        self.assertIsNone(texto)


if __name__ == "__main__":
    unittest.main()
