from execution.dao.conexao import ConexaoMongo
from execution.controller.classes import InteracaoBase


class DaoInteracao:
    """DAO para persistir interações no MongoDB"""
    _COLECAO = "interacoes"

    @classmethod
    def gravar(cls, interacao: InteracaoBase) -> None:
        """Grava uma interação no MongoDB"""
        banco = ConexaoMongo.get_banco()
        banco[cls._COLECAO].insert_one(interacao.model_dump(mode="json"))
