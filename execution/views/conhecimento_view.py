from pathlib import Path


class ConhecimentoView:
    """Renderiza a interface HTML da base de conhecimento."""

    _TEMPLATE = Path(__file__).parent / "html" / "conhecimento.html"

    @staticmethod
    def get(texto: str) -> str:
        """
        Lê o template HTML e injeta o texto da base de conhecimento.
        O texto é escapado para evitar problemas com caracteres especiais no HTML.
        """
        conteudo = ConhecimentoView._TEMPLATE.read_text(encoding="utf-8")
        # Escapa aspas e tags para uso seguro dentro do textarea
        texto_escapado = (
            texto
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        return conteudo.replace("{{TEXTO}}", texto_escapado)
