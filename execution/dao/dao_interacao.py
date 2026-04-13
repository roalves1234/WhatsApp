import asyncio

from loguru import logger

from execution.dao.conexao import ConexaoMongo
from execution.controller.classes import InteracaoBase


class DaoInteracao:
    """DAO para persistir interações no MongoDB"""
    _COLECAO = "interacoes"

    @classmethod
    async def persistir(cls, interacao: InteracaoBase) -> None:
        """Grava uma interação no MongoDB sem bloquear o event loop"""
        try:
            banco = ConexaoMongo.get_banco()
            await asyncio.to_thread(banco[cls._COLECAO].insert_one, interacao.model_dump(mode="json"))
        except Exception:
            logger.exception("DAO | Erro ao persistir | origem={origem} | fone={fone}", origem=interacao.origem, fone=interacao.fone)
            raise

    @classmethod
    async def get_by_fone(cls, fone: str) -> list[dict]:
        """
        Retorna lista de interações filtradas por fone, com origem e mensagem.
        O cursor pymongo é consumido dentro da thread para não bloquear o event loop.

        :param fone: Número de telefone para filtrar
        """
        try:
            banco = ConexaoMongo.get_banco()
            registros = await asyncio.to_thread(
                lambda: list(banco[cls._COLECAO].find({"fone": fone}))
            )
        except Exception:
            logger.exception("DAO | Erro ao buscar interações | fone={fone}", fone=fone)
            raise

        interacoes = [
            {"origem": doc["origem"], "mensagem": doc["mensagem"]}
            for doc in registros
        ]

        return interacoes

    @classmethod
    async def delete_by_fone(cls, fone: str) -> None:
        """
        Deleta todos os registros de um número de telefone sem bloquear o event loop.

        :param fone: Número de telefone para deletar
        """
        try:
            banco = ConexaoMongo.get_banco()
            await asyncio.to_thread(banco[cls._COLECAO].delete_many, {"fone": fone})
        except Exception:
            logger.exception("DAO | Erro ao deletar interações | fone={fone}", fone=fone)
            raise
