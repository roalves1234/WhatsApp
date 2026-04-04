from execution.dao.conexao import ConexaoMongo
from execution.controller.classes import InteracaoBase


class DaoInteracao:
    """DAO para persistir interações no MongoDB"""
    _COLECAO = "interacoes"

    @classmethod
    def persistir(cls, interacao: InteracaoBase) -> None:
        """Grava uma interação no MongoDB"""
        banco = ConexaoMongo.get_banco()
        banco[cls._COLECAO].insert_one(interacao.model_dump(mode="json"))

    @classmethod
    def get_by_fone(cls, fone: str) -> list[dict]:
        """
        Retorna lista de interações filtradas por fone, com origem e mensagem.

        :param fone: Número de telefone para filtrar
        """
        banco = ConexaoMongo.get_banco()
        registros = banco[cls._COLECAO].find({"fone": fone})

        interacoes = [
            {"origem": doc["origem"], "mensagem": doc["mensagem"]}
            for doc in registros
        ]

        return interacoes
