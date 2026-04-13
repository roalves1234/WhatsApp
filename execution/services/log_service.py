from datetime import date

from execution.rules.logs import LogFile


class LogService:
    """Serviço responsável pela consulta de logs."""

    @staticmethod
    def obter_lista_log(quantidade: int, data: date, nivel: str | None, fone: str | None) -> str:
        return LogFile.listar(quantidade=quantidade, data=data, nivel=nivel, fone=fone)

    @staticmethod
    def obter_lista_arquivos_log() -> dict[str, list[dict]]:
        return LogFile.listar_arquivos()
