import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from assistente_leilao.core import validator


class ValidatorTests(unittest.TestCase):
    def test_validar_url_aceita_http_e_https(self):
        self.assertIsNone(validator.validar_url("http://example.com"))
        self.assertIsNone(validator.validar_url("https://example.com/leilao"))

    def test_validar_url_rejeita_scheme_invalido(self):
        erro = validator.validar_url("ftp://example.com")
        self.assertEqual(erro, "URL inválida: scheme deve ser http ou https")

    def test_validar_url_rejeita_domino_vazio(self):
        erro = validator.validar_url("https:///sem-dominio")
        self.assertEqual(erro, "URL inválida: domínio (netloc) está vazio")

    def test_validar_timeout_aceita_inteiro_em_string(self):
        self.assertIsNone(validator.validar_timeout(" 15 "))

    def test_validar_timeout_rejeita_nao_numerico(self):
        erro = validator.validar_timeout("dez")
        self.assertEqual(erro, "Timeout inválido: deve ser um número inteiro")

    def test_validar_timeout_rejeita_zero_ou_negativo(self):
        self.assertEqual(
            validator.validar_timeout("0"),
            "Timeout inválido: deve ser maior que zero",
        )
        self.assertEqual(
            validator.validar_timeout(-5),
            "Timeout inválido: deve ser maior que zero",
        )

    def test_validar_nome_aceita_apenas_letras(self):
        self.assertIsNone(validator.validar_nome("Matheus"))

    def test_validar_nome_rejeita_curto_ou_com_numeros(self):
        self.assertEqual(
            validator.validar_nome("Al"),
            "Nome inválido: deve ter pelo menos 3 caracteres",
        )
        self.assertEqual(
            validator.validar_nome("Ana1"),
            "Nome inválido: deve conter apenas letras",
        )

    def test_validar_seletor_exige_xpath_ou_regex(self):
        self.assertEqual(
            validator.validar_seletor("", ""),
            "Seletor inválido: informe pelo menos xpath ou regex",
        )
        self.assertIsNone(validator.validar_seletor("//span", ""))
        self.assertIsNone(validator.validar_seletor("", r"R\\$ \\d+"))

    def test_validar_tudo_acumula_todos_os_erros(self):
        erros = validator.validar_tudo(
            "sem-url",
            "abc",
            "Ana1",
            "",
            "",
        )

        self.assertEqual(
            erros,
            [
                "URL inválida: scheme deve ser http ou https",
                "Timeout inválido: deve ser um número inteiro",
                "Nome inválido: deve conter apenas letras",
                "Seletor inválido: informe pelo menos xpath ou regex",
            ],
        )


if __name__ == "__main__":
    unittest.main()
