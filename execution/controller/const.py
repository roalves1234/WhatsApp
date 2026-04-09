import os


class UzapiConfig:
    """
    Classe de constantes para a integração com a API da Uzapi.
    """
    URL = "https://roalves1234.uazapi.com"
    TOKEN = "7d74751e-ea7d-4375-95a0-82ad1b069b72"

class LLM:
    """
    Classe de constantes para a integração com a LLM.
    """
    MODELO_ID = "gpt-4o-mini"


class SupabaseConfig:
    """
    Classe de constantes para a conexão com o Supabase.
    - URL / KEY: usadas pelo SDK Python (REST API).
    - DB_URL: connection string do PostgreSQL, montada a partir das variáveis do docker-compose.
    """
    URL = os.getenv("SUPABASE_URL", "")
    KEY = os.getenv("SUPABASE_KEY", "")

    # Conexão direta ao PostgreSQL (usada pelo PgVector)
    _PG_HOST = os.getenv("POSTGRES_HOST", "db")
    _PG_PORT = os.getenv("POSTGRES_PORT", "5432")
    _PG_DB = os.getenv("POSTGRES_DB", "postgres")
    _PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
    DB_URL = f"postgresql+psycopg://postgres:{_PG_PASSWORD}@{_PG_HOST}:{_PG_PORT}/{_PG_DB}"

