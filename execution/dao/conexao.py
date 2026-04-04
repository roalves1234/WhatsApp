from pymongo import MongoClient
from pymongo.database import Database


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
