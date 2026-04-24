import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def install_fake_browser_dependencies():
    selenium = types.ModuleType("selenium")
    webdriver = types.ModuleType("selenium.webdriver")
    chrome_module = types.ModuleType("selenium.webdriver.chrome")
    service_module = types.ModuleType("selenium.webdriver.chrome.service")
    webdriver_manager = types.ModuleType("webdriver_manager")
    chrome_manager_module = types.ModuleType("webdriver_manager.chrome")

    class ChromeOptions:
        def __init__(self):
            self.arguments = []

        def add_argument(self, argument):
            self.arguments.append(argument)

    class Service:
        def __init__(self, executable_path):
            self.executable_path = executable_path

    webdriver.ChromeOptions = ChromeOptions
    webdriver.Chrome = Mock()
    service_module.Service = Service

    manager_factory = Mock()
    manager_instance = Mock()
    manager_instance.install.return_value = "/tmp/chromedriver"
    manager_factory.return_value = manager_instance
    chrome_manager_module.ChromeDriverManager = manager_factory

    sys.modules["selenium"] = selenium
    sys.modules["selenium.webdriver"] = webdriver
    sys.modules["selenium.webdriver.chrome"] = chrome_module
    sys.modules["selenium.webdriver.chrome.service"] = service_module
    sys.modules["webdriver_manager"] = webdriver_manager
    sys.modules["webdriver_manager.chrome"] = chrome_manager_module

    return webdriver, manager_factory, manager_instance


def load_browser_module():
    webdriver, manager_factory, manager_instance = install_fake_browser_dependencies()
    sys.modules.pop("assistente_leilao.automation.browser", None)
    module = importlib.import_module("assistente_leilao.automation.browser")
    module.Browser._driver_path = None
    return module, webdriver, manager_factory, manager_instance


class BrowserTests(unittest.TestCase):
    def setUp(self):
        self.browser_module, self.webdriver, self.manager_factory, self.manager_instance = load_browser_module()

    def test_iniciar_reutiliza_driver_path_entre_instancias(self):
        first_driver = Mock()
        second_driver = Mock()
        self.webdriver.Chrome.side_effect = [first_driver, second_driver]

        browser_a = self.browser_module.Browser()
        browser_b = self.browser_module.Browser()

        browser_a.iniciar()
        browser_b.iniciar()

        self.manager_factory.assert_called_once_with()
        self.manager_instance.install.assert_called_once_with()
        self.assertEqual(self.webdriver.Chrome.call_count, 2)
        self.assertEqual(browser_a.driver, first_driver)
        self.assertEqual(browser_b.driver, second_driver)

        first_service = self.webdriver.Chrome.call_args_list[0].kwargs["service"]
        second_service = self.webdriver.Chrome.call_args_list[1].kwargs["service"]
        self.assertEqual(first_service.executable_path, "/tmp/chromedriver")
        self.assertEqual(second_service.executable_path, "/tmp/chromedriver")

    def test_iniciar_nao_recria_driver_na_mesma_instancia(self):
        first_driver = Mock()
        self.webdriver.Chrome.return_value = first_driver

        browser = self.browser_module.Browser()
        browser.iniciar()
        browser.iniciar()

        self.assertEqual(self.webdriver.Chrome.call_count, 1)
        self.manager_instance.install.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
