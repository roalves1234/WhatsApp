from execution.rules.arquivo_tool import ArquivoTool
from execution.views.arquivo_view import ArquivoView


class ArquivoService:
    """Serviço responsável pela montagem do visualizador de arquivos de log."""

    @staticmethod
    def obter_visualizador_arquivos(nome_arquivo: str | None) -> str:
        arquivos = ArquivoTool.listar()
        conteudo = ArquivoTool.ler_conteudo(nome_arquivo) if nome_arquivo else ""
        return ArquivoView.get(
            arquivos=arquivos,
            nome_selecionado=nome_arquivo,
            conteudo=conteudo,
        )
