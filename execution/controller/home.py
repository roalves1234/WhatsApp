import os


class Home:

    @staticmethod
    def get() -> str:
        """
        Lê o arquivo HTML da view e retorna seu conteúdo.
        Segue o padrão MVC: Controller buscando da View.
        """
        base_dir = os.path.join(os.path.dirname(__file__), "..")
        view_path = os.path.join(base_dir, "views", "index.html")
        version_path = os.path.join(base_dir, "version.txt")

        try:
            with open(view_path, "r", encoding="utf-8") as file:
                html_content = file.read()

            version = "Desconhecida"
            if os.path.exists(version_path):
                with open(version_path, "r", encoding="utf-8") as v_file:
                    version = v_file.read().strip()

            html_content = html_content.replace("{{VERSION}}", version)
            return html_content
        except Exception as e:
            return f"<h1>Error loading view: {str(e)}</h1>"
