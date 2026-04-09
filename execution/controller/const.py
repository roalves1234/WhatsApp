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
    Classe de constantes para a conexão direta ao PostgreSQL do Supabase (pgvector).
    A URL segue o formato: postgresql+psycopg://postgres.<ref>:<senha>@<host>:5432/postgres
    Disponível no painel Supabase > Settings > Database > Connection string (URI).
    """
    DB_URL = os.getenv("SUPABASE_DB_URL", "")

