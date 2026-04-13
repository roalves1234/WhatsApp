import asyncio

from execution.controller.base_vetorial import BaseVetorial
from execution.controller.conhecimento_view import ConhecimentoView
from execution.dao.dao_conhecimento import DaoConhecimento


class ConhecimentoService:
    """Serviço responsável pela base de conhecimento."""

    @staticmethod
    async def obter_conhecimento() -> str:
        texto = await DaoConhecimento.buscar_texto()
        return ConhecimentoView.get(texto)

    @staticmethod
    async def salvar_conhecimento(texto: str) -> dict[str, bool]:
        await DaoConhecimento.salvar_texto(texto)
        # atualizar() é síncrono e faz I/O bloqueante (OpenAI + Supabase),
        # por isso é executado em thread separada para não bloquear o event loop
        await asyncio.to_thread(BaseVetorial().atualizar, texto)
        return {"sucesso": True}
