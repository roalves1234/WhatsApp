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
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    MODELO_ID = "gpt-4o-mini"


class SupabaseConfig:
    """
    Classe de constantes para a conexão com o Supabase.
    - URL / KEY: usadas pelo SDK Python (REST API / PostgREST).
    """
    URL = os.getenv("SUPABASE_URL", "")
    KEY = os.getenv("SUPABASE_KEY", "")


class RAGConfig:
    """
    Classe de constantes compartilhadas pelo sistema de RAG
    (base vetorial + busca por similaridade).
    """
    MODELO_EMBEDDING = "text-embedding-3-small"
    NOME_FUNCAO_RPC = "match_documents"

