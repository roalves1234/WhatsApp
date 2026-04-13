from execution.views.home_view import HomeView


class HomeService:
    """Serviço responsável por carregar a view inicial."""

    @staticmethod
    def obter_home() -> str:
        return HomeView.get()
