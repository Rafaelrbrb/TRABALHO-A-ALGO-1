from __future__ import annotations

import logging


def configurar_logging(level: int = logging.INFO) -> None:
    logger = logging.getLogger("assistente_leilao")
    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )

    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
