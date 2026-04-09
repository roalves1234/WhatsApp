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

class Supabase:
    """
    Classe de constantes para a integração com o Supabase, lidas do .env.
    """
    import os
    URL = os.getenv("SUPABASE_URL", "")
    KEY = os.getenv("SUPABASE_KEY", "")

