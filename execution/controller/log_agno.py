import logging
from pathlib import Path

from agno.utils.log import configure_agno_logging


class LogAgno:
    """
    Responsável exclusivamente por configurar o logging do framework Agno em arquivo.

    Utiliza os loggers nomeados reconhecidos pelo Agno:
      - agno           → logs do Agent   → logs/agno_agent.log
      - agno-workflow  → logs do Workflow → logs/agno_workflow.log
    """

    _FORMATO = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    _LOG_DIR = Path("logs")

    _LOGGERS: list[tuple[str, str]] = [
        ("agno",          "logs/agno_agent.log"),
        ("agno-workflow", "logs/agno_workflow.log"),
    ]

    def __init__(self) -> None:
        self._LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._configurar_loggers()
        self._registrar_no_agno()

    def _criar_handler(self, caminho_arquivo: str) -> logging.FileHandler:
        """Cria e retorna um FileHandler formatado para o caminho informado."""
        handler = logging.FileHandler(caminho_arquivo, encoding="utf-8")
        handler.setFormatter(logging.Formatter(self._FORMATO))
        return handler

    def _configurar_loggers(self) -> None:
        """Adiciona FileHandler a cada logger nomeado e desativa propagação."""
        for nome_logger, caminho_arquivo in self._LOGGERS:
            logger = logging.getLogger(nome_logger)
            logger.setLevel(logging.DEBUG)
            logger.addHandler(self._criar_handler(caminho_arquivo))
            # Impede duplicatas no terminal via root logger
            logger.propagate = False

    def _registrar_no_agno(self) -> None:
        """Registra os loggers configurados no framework Agno."""
        configure_agno_logging(
            custom_agent_logger=logging.getLogger("agno"),
            custom_workflow_logger=logging.getLogger("agno-workflow"),
        )
