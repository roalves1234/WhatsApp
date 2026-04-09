from pymongo import MongoClient
from pymongo.database import Database
from supabase import Client, create_client

from execution.controller.const import Supabase


class ConexaoRestSupabase:
    """Responsável por fornecer conexões e URLs de acesso ao Supabase."""

    @staticmethod
    def url_tabela(tabela: str) -> str:
        """Retorna a URL REST da tabela informada."""
        return f"{Supabase.URL}/rest/v1/{tabela}"

    @staticmethod
    def cabecalhos() -> dict[str, str]:
        """Retorna os cabeçalhos de autenticação para a API REST do Supabase."""
        return {
            "apikey": Supabase.KEY,
            "Authorization": f"Bearer {Supabase.KEY}",
            "Content-Type": "application/json",
        }


class ConexaoSupabase:
    """Singleton para gerenciar o cliente Supabase (SDK Python / pgvector)."""
    _cliente: Client | None = None

    @classmethod
    def get_cliente(cls) -> Client:
        """Obtém o cliente Supabase, instanciando-o na primeira chamada."""
        if cls._cliente is None:
            cls._cliente = create_client(Supabase.URL, Supabase.KEY)
        return cls._cliente


class ConexaoMongo:
    """Singleton para gerenciar a conexão com MongoDB"""
    _cliente: MongoClient | None = None
    _STRING_CONEXAO = "mongodb://mongo:aswsde01@bd_mongo:27017/?tls=false"
    _NOME_BANCO = "WhatsApp"

    @classmethod
    def get_banco(cls) -> Database:
        """Obtém o banco de dados, instanciando o cliente na primeira chamada"""
        if cls._cliente is None:
            cls._cliente = MongoClient(cls._STRING_CONEXAO)
        return cls._cliente[cls._NOME_BANCO]
