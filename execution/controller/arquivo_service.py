from execution.controller.arquivo import Arquivo
from execution.controller.arquivo_view import ArquivoView


class ArquivoService:
    """Serviço responsável pela montagem do visualizador de arquivos de log."""

    @staticmethod
    def obter_visualizador_arquivos(nome_arquivo: str | None) -> str:
        arquivos = Arquivo.listar()
        conteudo = Arquivo.ler_conteudo(nome_arquivo) if nome_arquivo else ""
        return ArquivoView.get(
            arquivos=arquivos,
            nome_selecionado=nome_arquivo,
            conteudo=conteudo,
        )
