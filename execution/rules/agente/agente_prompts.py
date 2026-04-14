"""
Centraliza os prompts utilizados pelo agente, carregando-os a partir dos
arquivos .txt correspondentes e expondo-os como constantes de classe.
"""

from pathlib import Path

# Diretório onde este módulo e os arquivos de prompt residem
_DIRETORIO_ATUAL: Path = Path(__file__).resolve().parent


def _carregar_prompt(nome_arquivo: str) -> str:
    """Lê o conteúdo de um arquivo de prompt localizado no mesmo diretório deste módulo."""
    caminho: Path = _DIRETORIO_ATUAL / nome_arquivo
    return caminho.read_text(encoding="utf-8")


class Prompts:
    """Constantes com os prompts do agente já prontos para uso."""

    # Prompt da tool de base de conhecimento
    TOOL_BASE_CONHECIMENTO: str = _carregar_prompt("tool_base_conhecimento_prompt.txt")

    # Prompt do agente, com o placeholder {tool_base_conhecimento} já substituído
    AGENTE: str = _carregar_prompt("agente_prompt.txt").replace(
        "{tool_base_conhecimento}", TOOL_BASE_CONHECIMENTO
    )
