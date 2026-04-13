from pathlib import Path
from urllib.parse import quote

from execution.controller.arquivo import InfoArquivo


class ArquivoView:
    """Renderiza a interface HTML do visualizador de arquivos de log."""

    _TEMPLATE = Path(__file__).parent.parent / "views" / "visualizador-arquivos.html"

    @staticmethod
    def get(arquivos: list[InfoArquivo], nome_selecionado: str | None, conteudo: str) -> str:
        """
        Lê o template HTML e injeta a lista de botões e o conteúdo do arquivo selecionado.
        O conteúdo é escapado para evitar interpretação de tags pelo navegador.
        """
        html = ArquivoView._TEMPLATE.read_text(encoding="utf-8")

        botoes_html = ArquivoView._renderizar_botoes(arquivos, nome_selecionado)
        conteudo_escapado = ArquivoView._escapar_html(conteudo)

        html = html.replace("{{BOTOES}}", botoes_html)
        html = html.replace("{{NOME_ARQUIVO}}", nome_selecionado or "")
        html = html.replace("{{CONTEUDO}}", conteudo_escapado)
        html = html.replace("{{TOTAL}}", str(len(arquivos)))
        return html

    @staticmethod
    def _renderizar_botoes(arquivos: list[InfoArquivo], nome_selecionado: str | None) -> str:
        """Gera os links/botões da sidebar a partir da lista de arquivos."""
        if not arquivos:
            return '<p class="vazio">Nenhum arquivo encontrado.</p>'

        linhas: list[str] = []
        for info in arquivos:
            classe_ativo = " ativo" if info.nome == nome_selecionado else ""
            nome_url = quote(info.nome)
            tamanho_kb = max(1, info.tamanho // 1024)
            linhas.append(
                f'<a class="btn-arquivo{classe_ativo}" '
                f'href="/visualizador-arquivos?arquivo={nome_url}">'
                f'<span class="nome">{info.nome}</span>'
                f'<span class="meta">{tamanho_kb} KB</span>'
                f'</a>'
            )
        return "\n".join(linhas)

    @staticmethod
    def _escapar_html(texto: str) -> str:
        """Escapa caracteres especiais para exibição segura dentro de <pre>."""
        return (
            texto
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
