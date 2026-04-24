from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class Browser:
    _driver_path: str | None = None

    def __init__(self):
        self.driver = None

    @classmethod
    def obter_driver_path(cls) -> str:
        if cls._driver_path is None:
            cls._driver_path = ChromeDriverManager().install()
        return cls._driver_path

    def iniciar(self) -> None:
        if self.driver is not None:
            return

        service = Service(self.obter_driver_path())
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=service, options=options)

    def abrir_url(self, url: str) -> None:
        if self.driver is None:
            raise RuntimeError("Browser não iniciado. Chame iniciar() primeiro.")
        self.driver.get(url)

    def fechar(self) -> None:
        if self.driver is not None:
            self.driver.quit()
            self.driver = None

    def obter_driver(self):
        if self.driver is None:
            raise RuntimeError("Browser não iniciado. Chame iniciar() primeiro.")
        return self.driver
