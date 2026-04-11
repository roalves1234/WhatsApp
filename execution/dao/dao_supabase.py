from sqlalchemy import create_engine, text
from loguru import logger

from execution.controller.const import SupabaseConfig


class DaoSupabase:
    """DAO responsável por operações de diagnóstico no PostgreSQL do Supabase."""

    @staticmethod
    def testar_conexao() -> dict[str, str]:
        """
        Testa a conexão com o PostgreSQL e retorna o host utilizado e a versão do banco.
        Em caso de falha, retorna o erro capturado.
        """
        try:
            engine = create_engine(SupabaseConfig.DB_URL)
            with engine.connect() as conn:
                resultado = conn.execute(text("SELECT version()"))
                versao = resultado.scalar()
            engine.dispose()

            logger.info("SUPABASE | Conexão OK | host={host}", host=SupabaseConfig._PG_HOST)
            return {"status": "ok", "host": SupabaseConfig._PG_HOST, "versao": versao}

        except Exception as e:
            logger.error("SUPABASE | Falha na conexão | host={host} | erro={erro}", host=SupabaseConfig._PG_HOST, erro=str(e))
            return {"status": "erro", "host": SupabaseConfig._PG_HOST, "erro": str(e)}
