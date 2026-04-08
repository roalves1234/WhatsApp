import os

import httpx
from loguru import logger

# URL base e chave anônima do Supabase, lidas do .env
_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
_TABELA = "base_conhecimento"


def _cabecalhos() -> dict[str, str]:
    """Retorna os cabeçalhos obrigatórios para autenticação na API REST do Supabase."""
    return {
        "apikey": _SUPABASE_KEY,
        "Authorization": f"Bearer {_SUPABASE_KEY}",
        "Content-Type": "application/json",
    }


class DaoConhecimento:
    """DAO responsável por ler e gravar a base de conhecimento no Supabase."""

    @staticmethod
    async def buscar_texto() -> str:
        """
        Busca o campo 'texto' do primeiro registro da tabela base_conhecimento.
        Retorna string vazia se a tabela estiver sem registros.
        """
        url = f"{_SUPABASE_URL}/rest/v1/{_TABELA}?select=texto&limit=1"
        async with httpx.AsyncClient() as cliente:
            resposta = await cliente.get(url, headers=_cabecalhos())
            resposta.raise_for_status()
            dados: list[dict] = resposta.json()

        texto = dados[0].get("texto", "") if dados else ""
        logger.debug("CONHECIMENTO | Texto carregado | tamanho={n} chars", n=len(texto))
        return texto

    @staticmethod
    async def salvar_texto(texto: str) -> None:
        """
        Atualiza o campo 'texto' do primeiro registro da tabela base_conhecimento.
        Se não existir nenhum registro, insere um novo.
        """
        url_base = f"{_SUPABASE_URL}/rest/v1/{_TABELA}"

        async with httpx.AsyncClient() as cliente:
            # Busca o id do primeiro registro para montar o filtro do PATCH
            resposta_id = await cliente.get(
                f"{url_base}?select=id&limit=1",
                headers=_cabecalhos(),
            )
            resposta_id.raise_for_status()
            dados: list[dict] = resposta_id.json()

            if dados:
                id_registro = dados[0]["id"]
                resposta = await cliente.patch(
                    f"{url_base}?id=eq.{id_registro}",
                    headers=_cabecalhos(),
                    json={"texto": texto},
                )
            else:
                # Cria o primeiro registro caso a tabela esteja vazia
                resposta = await cliente.post(
                    url_base,
                    headers=_cabecalhos(),
                    json={"texto": texto},
                )

        resposta.raise_for_status()
        logger.info("CONHECIMENTO | Texto salvo | tamanho={n} chars", n=len(texto))
