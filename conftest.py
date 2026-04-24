"""
Configuração pytest para testes do assistente de leilão

Este arquivo configura fixtures e comportamentos globais para todos os testes.
"""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def driver_mock():
    """Fixture que fornece um mock de WebDriver"""
    return MagicMock()


@pytest.fixture
def timeout_default():
    """Timeout padrão para testes"""
    return 10


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset de módulos entre testes para evitar estado compartilhado"""
    yield
    # Limpa após cada teste se necessário


# Configurações globais
def pytest_configure(config):
    """Configuração global do pytest"""
    config.addinivalue_line(
        "markers", "unit: marca testes unitários"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "slow: marca testes lentos"
    )


# Hook para relatório mais verboso
def pytest_collection_modifyitems(config, items):
    """Modifica items coletados para adicionar markers automáticos"""
    for item in items:
        # Adiciona marker unit por padrão
        if "test_" in item.nodeid and "tests" in item.nodeid:
            item.add_marker(pytest.mark.unit)
