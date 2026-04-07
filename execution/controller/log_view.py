import os
from datetime import date


class LogView:

    @staticmethod
    def get(registros: list[dict], quantidade: int, data: date, nivel: str | None, fone: str | None) -> str:
        """
        Renderiza a view HTML do grid de logs a partir dos registros parseados
        e dos filtros ativos, que são pré-preenchidos no formulário.
        """
        base_dir = os.path.join(os.path.dirname(__file__), "..")
        view_path = os.path.join(base_dir, "views", "logs.html")

        with open(view_path, "r", encoding="utf-8") as arquivo:
            html = arquivo.read()

        linhas_html = LogView._renderizar_linhas(registros)

        # Pré-seleciona o nível no dropdown
        for opcao in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            selecionado = "selected" if nivel and nivel.upper() == opcao else ""
            html = html.replace(f"{{{{SEL_{opcao}}}}}", selecionado)

        html = html.replace("{{LINHAS}}", linhas_html)
        html = html.replace("{{QUANTIDADE}}", str(quantidade))
        html = html.replace("{{DATA}}", str(data))
        html = html.replace("{{FONE}}", fone or "")
        html = html.replace("{{TOTAL}}", str(len(registros)))
        return html

    @staticmethod
    def _renderizar_linhas(registros: list[dict]) -> str:
        """Gera as linhas <tr> da tabela a partir dos registros."""
        if not registros:
            return '<tr><td colspan="4" class="vazio">Nenhum registro encontrado.</td></tr>'

        linhas: list[str] = []
        for r in registros:
            nivel_css = r["nivel"].lower().split()[0]  # ex: "ERROR   " → "error"
            # Escapa HTML básico da mensagem e preserva quebras de linha do traceback
            mensagem_escapada = (
                r["mensagem"]
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\n", "<br>")
            )
            linhas.append(
                f'<tr class="nivel-{nivel_css}">'
                f'<td class="col-data">{r["data_hora"]}</td>'
                f'<td class="col-nivel"><span class="badge badge-{nivel_css}">{r["nivel"]}</span></td>'
                f'<td class="col-local">{r["local"]}</td>'
                f'<td class="col-msg">{mensagem_escapada}</td>'
                f"</tr>"
            )
        return "\n".join(linhas)
