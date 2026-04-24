import pytest
from assistente_leilao.core.validator import (
    validar_url,
    validar_timeout,
    validar_nome,
    validar_seletor,
    validar_tudo
)


class TestValidarUrl:
    """Testes para validação de URL"""
    
    def test_url_valida_http(self):
        """URL válida com HTTP"""
        resultado = validar_url("http://example.com")
        assert resultado is None
    
    def test_url_valida_https(self):
        """URL válida com HTTPS"""
        resultado = validar_url("https://example.com")
        assert resultado is None
    
    def test_url_com_espacos(self):
        """URL com espaços em branco"""
        resultado = validar_url("  https://example.com  ")
        assert resultado is None
    
    def test_url_scheme_invalido(self):
        """URL com scheme inválido"""
        resultado = validar_url("ftp://example.com")
        assert "scheme deve ser http ou https" in resultado
    
    def test_url_sem_scheme(self):
        """URL sem scheme"""
        resultado = validar_url("example.com")
        assert "scheme deve ser http ou https" in resultado
    
    def test_url_sem_dominio(self):
        """URL sem domínio"""
        resultado = validar_url("http://")
        assert "domínio (netloc) está vazio" in resultado
    
    def test_url_vazia(self):
        """URL vazia"""
        resultado = validar_url("")
        assert resultado is not None


class TestValidarTimeout:
    """Testes para validação de timeout"""
    
    def test_timeout_valido_inteiro(self):
        """Timeout válido como inteiro"""
        resultado = validar_timeout(5)
        assert resultado is None
    
    def test_timeout_valido_string(self):
        """Timeout válido como string"""
        resultado = validar_timeout("10")
        assert resultado is None
    
    def test_timeout_com_espacos(self):
        """Timeout string com espaços"""
        resultado = validar_timeout("  15  ")
        assert resultado is None
    
    def test_timeout_invalido_string(self):
        """Timeout string inválida"""
        resultado = validar_timeout("abc")
        assert "deve ser um número inteiro" in resultado
    
    def test_timeout_zero(self):
        """Timeout com valor zero"""
        resultado = validar_timeout(0)
        assert "deve ser maior que zero" in resultado
    
    def test_timeout_negativo(self):
        """Timeout com valor negativo"""
        resultado = validar_timeout(-5)
        assert "deve ser maior que zero" in resultado
    
    def test_timeout_float(self):
        """Timeout como float"""
        resultado = validar_timeout(5.5)
        assert resultado is None or "número inteiro" in resultado


class TestValidarNome:
    """Testes para validação de nome"""
    
    def test_nome_valido(self):
        """Nome válido"""
        resultado = validar_nome("João")
        assert resultado is None
    
    def test_nome_com_espacos(self):
        """Nome com espaços"""
        resultado = validar_nome("  Maria  ")
        assert resultado is None
    
    def test_nome_muito_curto(self):
        """Nome com menos de 3 caracteres"""
        resultado = validar_nome("Jo")
        assert "deve ter pelo menos 3 caracteres" in resultado
    
    def test_nome_vazio(self):
        """Nome vazio"""
        resultado = validar_nome("")
        assert "deve ter pelo menos 3 caracteres" in resultado
    
    def test_nome_com_numeros(self):
        """Nome com números"""
        resultado = validar_nome("João123")
        assert "deve conter apenas letras" in resultado
    
    def test_nome_com_especiais(self):
        """Nome com caracteres especiais"""
        resultado = validar_nome("João@#$")
        assert "deve conter apenas letras" in resultado
    
    def test_nome_com_acentos(self):
        """Nome com acentos"""
        resultado = validar_nome("José")
        # Acentos são letras, então deve ser válido
        assert resultado is None


class TestValidarSeletor:
    """Testes para validação de seletor (xpath ou regex)"""
    
    def test_seletor_valido_xpath(self):
        """Seletor válido com xpath"""
        resultado = validar_seletor("//div[@class='preco']", "")
        assert resultado is None
    
    def test_seletor_valido_regex(self):
        """Seletor válido com regex"""
        resultado = validar_seletor("", r"\d+\.\d{2}")
        assert resultado is None
    
    def test_seletor_ambos_validos(self):
        """Ambos xpath e regex informados"""
        resultado = validar_seletor("//div", r"\d+")
        assert resultado is None
    
    def test_seletor_ambos_vazios(self):
        """Ambos xpath e regex vazios"""
        resultado = validar_seletor("", "")
        assert "informe pelo menos xpath ou regex" in resultado
    
    def test_seletor_xpath_none(self):
        """Xpath como None"""
        resultado = validar_seletor(None, r"\d+")
        # Pode gerar erro ou aceitar
        assert resultado is None or "xpath" in resultado


class TestValidarTudo:
    """Testes para validação combinada de todos os campos"""
    
    def test_validacao_tudo_valido(self):
        """Todos os campos válidos"""
        erros = validar_tudo(
            url="https://example.com",
            timeout=5,
            nome="João",
            xpath="//div[@class='preco']",
            regex=""
        )
        assert len(erros) == 0
    
    def test_validacao_tudo_invalido(self):
        """Todos os campos inválidos"""
        erros = validar_tudo(
            url="ftp://",
            timeout=-1,
            nome="Jo",
            xpath="",
            regex=""
        )
        assert len(erros) > 0
        assert len(erros) == 4  # 4 erros esperados
    
    def test_validacao_multiplos_erros(self):
        """Alguns campos inválidos"""
        erros = validar_tudo(
            url="http://example.com",  # válido
            timeout=0,  # inválido
            nome="Maria",  # válido
            xpath="//",  # válido
            regex=""  # regex vazio (válido pois xpath foi informado)
        )
        assert len(erros) == 1  # apenas timeout inválido
        assert "Timeout inválido" in erros[0]
    
    def test_validacao_retorna_lista(self):
        """Valida que o retorno é sempre uma lista"""
        erros = validar_tudo(
            url="https://example.com",
            timeout=10,
            nome="Pedro",
            xpath="//span",
            regex=""
        )
        assert isinstance(erros, list)