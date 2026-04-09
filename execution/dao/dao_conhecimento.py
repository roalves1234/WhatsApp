import httpx
from loguru import logger

from execution.dao.conexao import ConexaoRestSupabase

class DaoConhecimento:
    """DAO responsável por ler e gravar a base de conhecimento no Supabase."""

    _TABELA = "base_conhecimento"
    _URL_BASE = ConexaoRestSupabase.url_tabela(_TABELA)

    @staticmethod
    async def buscar_texto() -> str:
        """Busca o campo 'texto' do primeiro registro da tabela base_conhecimento.
        Retorna string vazia se a tabela estiver sem registros.
        """
        async with httpx.AsyncClient() as cliente:
            resposta = await cliente.get(
                f"{DaoConhecimento._URL_BASE}?select=texto&limit=1",
                headers=ConexaoRestSupabase.cabecalhos(),
            )
            resposta.raise_for_status()
            dados: list[dict] = resposta.json()

        texto = dados[0].get("texto", "") if dados else ""
        logger.debug("CONHECIMENTO | Texto carregado | tamanho={n} chars", n=len(texto))
        return texto

    @staticmethod
    async def _buscar_id_registro() -> str | None:
        """Retorna o id do primeiro registro existente, ou None se a tabela estiver vazia."""
        async with httpx.AsyncClient() as cliente:
            resposta = await cliente.get(
                f"{DaoConhecimento._URL_BASE}?select=id&limit=1",
                headers=ConexaoRestSupabase.cabecalhos(),
            )
            resposta.raise_for_status()
            dados: list[dict] = resposta.json()

        return dados[0]["id"] if dados else None

    @staticmethod
    async def _atualizar_texto(id_registro: str, texto: str) -> None:
        """Atualiza o campo 'texto' do registro identificado por id_registro via PATCH."""
        async with httpx.AsyncClient() as cliente:
            resposta = await cliente.patch(
                f"{DaoConhecimento._URL_BASE}?id=eq.{id_registro}",
                headers=ConexaoRestSupabase.cabecalhos(),
                json={"texto": texto},
            )
            resposta.raise_for_status()

    @staticmethod
    async def _inserir_texto(texto: str) -> None:
        """Insere um novo registro com o campo 'texto' via POST."""
        async with httpx.AsyncClient() as cliente:
            resposta = await cliente.post(
                DaoConhecimento._URL_BASE,
                headers=ConexaoRestSupabase.cabecalhos(),
                json={"texto": texto},
            )
            resposta.raise_for_status()

    @staticmethod
    async def salvar_texto(texto: str) -> None:
        """Persiste o texto na tabela: atualiza o registro existente ou insere um novo."""
        id_registro = await DaoConhecimento._buscar_id_registro()

        if id_registro:
            await DaoConhecimento._atualizar_texto(id_registro, texto)
        else:
            await DaoConhecimento._inserir_texto(texto)

        logger.info("CONHECIMENTO | Texto salvo | tamanho={n} chars", n=len(texto))
