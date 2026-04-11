from execution.dao.dao_supabase import DaoSupabase


class SupabaseService:
    """Serviço responsável por operações relacionadas ao Supabase."""

    @staticmethod
    def testar_conexao() -> dict[str, str]:
        return DaoSupabase.testar_conexao()
