from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class InfoArquivo:
    """Metadados de um arquivo listado."""
    nome: str
    tamanho: int
    data_modificacao: datetime


class ArquivoTool:
    """Camada DAO genérica para operações sobre arquivos de um diretório."""

    @staticmethod
    def listar(diretorio: Path, extensoes: set[str]) -> list[InfoArquivo]:
        """Lista arquivos do diretório cujas extensões estejam em `extensoes`, ordenados por data desc."""
        if not diretorio.exists():
            return []

        arquivos: list[InfoArquivo] = []
        for caminho in diretorio.iterdir():
            if not caminho.is_file():
                continue
            if caminho.suffix not in extensoes:
                continue
            estatisticas = caminho.stat()
            arquivos.append(
                InfoArquivo(
                    nome=caminho.name,
                    tamanho=estatisticas.st_size,
                    data_modificacao=datetime.fromtimestamp(estatisticas.st_mtime),
                )
            )

        arquivos.sort(key=lambda info: info.data_modificacao, reverse=True)
        return arquivos

    @staticmethod
    def ler_conteudo(caminho: Path) -> str:
        """Fachada pública — delega para a classe interna de leitura."""
        return ArquivoTool._ArquivoLeitura.ler_conteudo(caminho=caminho)

    class _ArquivoLeitura:
        """Classe aninhada privada que concentra toda a lógica de leitura de arquivos."""

        _TAMANHO_MAXIMO_BYTES: int = 5_000_000

        @staticmethod
        def ler_conteudo(caminho: Path) -> str:
            """
            Lê o conteúdo bruto de um arquivo.
            Retorna texto não escapado — a camada View é responsável pelo escape HTML.
            """
            if not caminho.exists() or not caminho.is_file():
                return "[Arquivo não encontrado]"

            tamanho = caminho.stat().st_size

            if tamanho > ArquivoTool._ArquivoLeitura._TAMANHO_MAXIMO_BYTES:
                return ArquivoTool._ArquivoLeitura._ler_final_arquivo(
                    caminho=caminho, tamanho_total=tamanho
                )

            return caminho.read_text(encoding="utf-8", errors="replace")

        @staticmethod
        def _ler_final_arquivo(caminho: Path, tamanho_total: int) -> str:
            """Lê apenas os últimos N bytes de um arquivo grande, prefixando um banner de truncagem."""
            with caminho.open("rb") as arquivo_binario:
                arquivo_binario.seek(-ArquivoTool._ArquivoLeitura._TAMANHO_MAXIMO_BYTES, 2)
                bytes_finais = arquivo_binario.read()
            conteudo = bytes_finais.decode("utf-8", errors="replace")
            banner = (
                f"[ARQUIVO TRUNCADO - exibindo últimos "
                f"{ArquivoTool._ArquivoLeitura._TAMANHO_MAXIMO_BYTES // 1_000_000} MB de "
                f"{tamanho_total // 1_000_000} MB]\n\n"
            )
            return banner + conteudo
