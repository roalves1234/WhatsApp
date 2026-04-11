from threading import Lock

from loguru import logger
from pymongo import MongoClient
from pymongo.database import Database
from supabase import Client, create_client

from execution.controller.const import SupabaseConfig


class ConexaoSupabase:
    """Singleton para gerenciar o cliente Supabase (SDK Python / pgvector)."""

    _cliente: Client | None = None
    _lock_inicializacao: Lock = Lock()
    _TABELA_TESTE = "base_conhecimento"

    @classmethod
    def get_cliente(cls) -> Client:
        """Obtém o cliente Supabase, instanciando-o na primeira chamada."""
        if cls._cliente is None:
            # Evita condição de corrida na primeira criação do cliente.
            with cls._lock_inicializacao:
                if cls._cliente is None:
                    cls._cliente = create_client(SupabaseConfig.URL, SupabaseConfig.KEY)
        return cls._cliente

    @classmethod
    def testar_conexao(cls) -> dict[str, str]:
        """
        Testa a conexão com o Supabase via SDK (REST/PostgREST) executando uma
        consulta leve na tabela de referência. Retorna success ou fail.
        """
        try:
            cliente = cls.get_cliente()
            # Consulta mínima apenas para validar que a API REST responde.
            cliente.table(cls._TABELA_TESTE).select("id").limit(1).execute()
            logger.info("SUPABASE | Conexão SDK OK | url={url}", url=SupabaseConfig.URL)
            return {"result": "success"}

        except Exception as e:
            logger.error("SUPABASE | Falha na conexão SDK | url={url} | erro={erro}", url=SupabaseConfig.URL, erro=str(e))
            return {"result": "fail"}


class ConexaoMongo:
    """Singleton para gerenciar a conexão com MongoDB."""

    _cliente: MongoClient | None = None
    _lock_inicializacao: Lock = Lock()
    _STRING_CONEXAO = "mongodb://mongo:aswsde01@bd_mongo:27017/?tls=false"
    _NOME_BANCO = "WhatsApp"
    _TAMANHO_MINIMO_POOL = 5
    _TAMANHO_MAXIMO_POOL = 20
    _TEMPO_MAXIMO_OCIOSO_MS = 30000
    _TEMPO_ESPERA_FILA_MS = 10000

    @classmethod
    def get_banco(cls) -> Database:
        """Obtém o banco de dados, instanciando o cliente na primeira chamada."""
        if cls._cliente is None:
            # Evita condição de corrida na primeira criação do cliente.
            with cls._lock_inicializacao:
                if cls._cliente is None:
                    cls._cliente = MongoClient(
                        cls._STRING_CONEXAO,
                        minPoolSize=cls._TAMANHO_MINIMO_POOL,
                        maxPoolSize=cls._TAMANHO_MAXIMO_POOL,
                        maxIdleTimeMS=cls._TEMPO_MAXIMO_OCIOSO_MS,
                        waitQueueTimeoutMS=cls._TEMPO_ESPERA_FILA_MS,
                    )
        return cls._cliente[cls._NOME_BANCO]
