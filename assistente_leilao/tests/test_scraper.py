import importlib
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

def load_scraper_module():
    fake_page_finder = types.ModuleType("assistente_leilao.automation.page_finder")
    fake_page_finder.encontrar_valor = Mock(return_value=None)
    sys.modules["assistente_leilao.automation.page_finder"] = fake_page_finder
    sys.modules.pop("assistente_leilao.core.scraper", None)
    return importlib.import_module("assistente_leilao.core.scraper")


class ScraperTests(unittest.TestCase):
    def setUp(self):
        self.scraper = load_scraper_module()

    def test_extrair_numero_converte_formato_brasileiro(self):
        valor = self.scraper.extrair_numero("R$ 1.234,56")
        self.assertAlmostEqual(valor, 1234.56)

    def test_extrair_numero_retorna_none_para_texto_invalido(self):
        self.assertIsNone(self.scraper.extrair_numero("sem preco"))

    def test_extrair_numero_aceita_ponto_como_decimal(self):
        valor = self.scraper.extrair_numero("R$ 12.50")
        self.assertAlmostEqual(valor, 12.50)

    def test_obter_preco_retorna_none_quando_nao_encontra_texto(self):
        driver = object()
        self.scraper.encontrar_valor = Mock(return_value=None)

        valor = self.scraper.obter_preco(driver, "//span", "")

        self.assertIsNone(valor)
        self.scraper.encontrar_valor.assert_called_once_with(driver, "//span", "")

    def test_obter_preco_converte_texto_encontrado(self):
        driver = object()
        self.scraper.encontrar_valor = Mock(return_value="R$ 99,90")

        valor = self.scraper.obter_preco(driver, "//span", "")

        self.assertAlmostEqual(valor, 99.90)
        self.scraper.encontrar_valor.assert_called_once_with(driver, "//span", "")


if __name__ == "__main__":
    unittest.main()
