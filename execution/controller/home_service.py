from execution.controller.home import Home


class HomeService:
    """Serviço responsável por carregar a view inicial."""

    @staticmethod
    def obter_home() -> str:
        return Home.get()
