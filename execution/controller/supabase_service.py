from execution.dao.conexao import ConexaoSupabase


class SupabaseService:
    """Serviço responsável por operações relacionadas ao Supabase."""

    @staticmethod
    def testar_conexao() -> dict[str, str]:
        return ConexaoSupabase.testar_conexao()
