from pathlib import Path

from execution.comum.arquivo_tool import ArquivoTool
from execution.views.arquivo_view import ArquivoView


class ArquivoService:
    """Serviço responsável pela montagem do visualizador de arquivos de log."""

    # Configurações específicas deste caso de uso — o DAO é genérico
    _DIR_LOGS: Path = Path(__file__).parent.parent.parent / "logs"
    _EXTENSOES_PERMITIDAS: set[str] = {".log", ".agno"}

    @staticmethod
    def obter_visualizador_arquivos(nome_arquivo: str | None) -> str:
        arquivos = ArquivoTool.listar(
            diretorio=ArquivoService._DIR_LOGS,
            extensoes=ArquivoService._EXTENSOES_PERMITIDAS,
        )

        conteudo = ""
        if nome_arquivo:
            caminho = ArquivoService._DIR_LOGS / nome_arquivo
            conteudo = ArquivoTool.ler_conteudo(caminho=caminho)

        return ArquivoView.get(
            arquivos=arquivos,
            nome_selecionado=nome_arquivo,
            conteudo=conteudo,
        )
