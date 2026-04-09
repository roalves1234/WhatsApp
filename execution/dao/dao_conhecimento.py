import asyncio
from loguru import logger
from execution.dao.conexao import ConexaoSupabase


class DaoConhecimento:
    """DAO responsável por ler e gravar a base de conhecimento no Supabase."""

    _TABELA = "base_conhecimento"

    @staticmethod
    async def buscar_texto() -> str:
        """Busca o campo 'texto' do primeiro registro da tabela base_conhecimento.
        Retorna string vazia se a tabela estiver sem registros.
        """
        def _executar():
            cliente = ConexaoSupabase.get_cliente()
            resposta = cliente.table(DaoConhecimento._TABELA).select("texto").limit(1).execute()
            return resposta.data

        dados: list[dict] = await asyncio.to_thread(_executar)
        texto = dados[0].get("texto", "") if dados else ""
        logger.debug("CONHECIMENTO | Texto carregado | tamanho={n} chars", n=len(texto))
        return texto

    @staticmethod
    async def _buscar_id_registro() -> str | None:
        """Retorna o id do primeiro registro existente, ou None se a tabela estiver vazia."""
        def _executar():
            cliente = ConexaoSupabase.get_cliente()
            resposta = cliente.table(DaoConhecimento._TABELA).select("id").limit(1).execute()
            return resposta.data

        dados: list[dict] = await asyncio.to_thread(_executar)
        return dados[0]["id"] if dados else None

    @staticmethod
    async def _atualizar_texto(id_registro: str, texto: str) -> None:
        """Atualiza o campo 'texto' do registro identificado por id_registro."""
        def _executar():
            cliente = ConexaoSupabase.get_cliente()
            cliente.table(DaoConhecimento._TABELA).update({"texto": texto}).eq("id", id_registro).execute()

        await asyncio.to_thread(_executar)

    @staticmethod
    async def _inserir_texto(texto: str) -> None:
        """Insere um novo registro com o campo 'texto'."""
        def _executar():
            cliente = ConexaoSupabase.get_cliente()
            cliente.table(DaoConhecimento._TABELA).insert({"texto": texto}).execute()

        await asyncio.to_thread(_executar)

    @staticmethod
    async def salvar_texto(texto: str) -> None:
        """Persiste o texto na tabela: atualiza o registro existente ou insere um novo."""
        id_registro = await DaoConhecimento._buscar_id_registro()

        if id_registro:
            await DaoConhecimento._atualizar_texto(id_registro, texto)
        else:
            await DaoConhecimento._inserir_texto(texto)

        logger.info("CONHECIMENTO | Texto salvo | tamanho={n} chars", n=len(texto))
