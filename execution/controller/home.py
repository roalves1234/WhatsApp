import os

from execution.controller.version import Version


class Home:

    @staticmethod
    def get() -> str:
        """
        Lê o arquivo HTML da view e retorna seu conteúdo.
        Segue o padrão MVC: Controller buscando da View.
        """
        base_dir = os.path.join(os.path.dirname(__file__), "..")
        view_path = os.path.join(base_dir, "views", "index.html")

        try:
            with open(view_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            version = Version().get()
            html_content = html_content.replace("{{VERSION}}", version)
            return html_content
        except Exception as e:
            return f"<h1>Error loading view: {str(e)}</h1>"
