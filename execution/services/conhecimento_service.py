import asyncio

from execution.rules.base_vetorial import BaseVetorial
from execution.views.conhecimento_view import ConhecimentoView
from execution.dao.conhecimento_dao import ConhecimentoDao


class ConhecimentoService:
    """Serviço responsável pela base de conhecimento."""

    @staticmethod
    async def obter_conhecimento() -> str:
        texto = await ConhecimentoDao.buscar_texto()
        return ConhecimentoView.get(texto)

    @staticmethod
    async def salvar_conhecimento(texto: str) -> dict[str, bool]:
        await ConhecimentoDao.salvar_texto(texto)
        # atualizar() é síncrono e faz I/O bloqueante (OpenAI + Supabase),
        # por isso é executado em thread separada para não bloquear o event loop
        await asyncio.to_thread(BaseVetorial().atualizar, texto)
        return {"sucesso": True}
